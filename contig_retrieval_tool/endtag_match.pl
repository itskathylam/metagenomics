#!/usr/bin/perl
use warnings;
use strict;

use lib '/usr/share/perl5';
#use lib '/usr/bin/emboss/emboss';
use lib '/usr/lib/cpan/build/';
use lib '/usr/lib/cpan/custom/BioPerl-SABP/lib/';
use lib '/usr/lib/cpan/custom/BioPerl';
use lib '/usr/lib/cpan/custom/Storable/blib/lib/';
use Bio::Seq;
use Bio::Tools::Run::StandAloneBlastPlus;
use Spreadsheet::ParseExcel;
use Spreadsheet::WriteExcel;
use Bio::AlignIO;
use Bio::SearchIO;
use Bio::SeqIO;
#use Bio::Factory::EMBOSS;
use Data::Dumper;
use File::Path qw/make_path remove_tree/;
use Storable;
use Cwd 'chdir';
#$" = "\n";

my %contig_orf;
if (scalar(@ARGV) == 2) {
     
    #-----------------------------------------------------------------------#
    #                                                                       #
    #                       Set Parameters                                  #
    #                                                                       #
    #-----------------------------------------------------------------------#

     my $sig_level = 0.65; 
    #-----------------------------------------------------------------------#
    #                   Private Variables                                   #
    #-----------------------------------------------------------------------#
    
    my $parentid = $ARGV[0];
    my $cwd = $ARGV[1];
    chdir("$cwd");
    my $_contig_retrieval = retrieve("temp/storage/write.$parentid") or die "Could not retrieve $!\n";
    my %_contig_retrieval = %{$_contig_retrieval};
    my $row_count = 0;
    my %_graphic_output;
    open(my $_outcsv, ">>", "tmp/out/retrieval.csv") or die "Could not export to CSV file, $!\n";

    
    
    #--------------------------------------------------------------------------
    #-----------------DETERMINING MATCHES AND SIGNIFICANCE---------------------
    #--------------------------------------------------------------------------
    
    #This step will determine whether the contig retrieved from the local database BLAST
    # is of any significance.  It will filter out spurious elements that aligned and will
    # report whether both the F_ and R_ retrieved the same contig, whether they retrieved
    # different contigs, or whether there was a significant ambiguity that warrants
    # further investigation.
    
    my (@temp_cnt, @temp_hit, @temp_eval, @temp_len, @temp_qlen);
    my (@flag_storage);
    my %comp_storage;
    
    # Loop through every key of the hash %_contig_retrieval
    #
    # Creates a hash, comp_storage with the direction of the end tag sequence (i.e. F_ or R_) appropriately
    # Extracts direction count (i.e. F_1, F_2, F_3), hit_name (i.e. scaffold_781), e-value, hit_length, and query_length
    # and stores them in their own respective arrays that will be found under the comp_storage
    # F_ or R_ hash.
    foreach my $temp_query(sort keys(%_contig_retrieval)){
        my $_tf = "R";
        foreach my $temp_rf(sort keys($_contig_retrieval{$temp_query})){
            if ($temp_rf =~/$_tf/) {
                $_tf = "F";
                $comp_storage{$_tf} = [[@temp_cnt], [@temp_hit], [@temp_eval], [@temp_len], [@temp_qlen]];
                (@temp_cnt, @temp_hit, @temp_eval, @temp_len, @temp_qlen) = ();
            }
            push(@temp_cnt, $temp_rf);                                          #0   e.g. F_1
            push(@temp_hit, $_contig_retrieval{$temp_query}{$temp_rf}->[1]);    #1   Hit name      i.e. lsl|scaffold751_3
            push(@temp_eval, $_contig_retrieval{$temp_query}{$temp_rf}->[3]);   #2   Blast e-value
            push(@temp_len, $_contig_retrieval{$temp_query}{$temp_rf}->[7]);    #3   HSP length
            push(@temp_qlen, $_contig_retrieval{$temp_query}{$temp_rf}->[6]);   #4   Length of the end-tag query sequence
            
        }
        if($_tf =~ /R/){
            $_tf = "F";
            $comp_storage{$_tf} = [[@temp_cnt], [@temp_hit], [@temp_eval], [@temp_len], [@temp_qlen]];
            (@temp_cnt, @temp_hit, @temp_eval, @temp_len, @temp_qlen) = ();
        } elsif ($_tf =~ /F/) {
            $_tf = "R";
            $comp_storage{$_tf} = [[@temp_cnt], [@temp_hit], [@temp_eval], [@temp_len], [@temp_qlen]];
            (@temp_cnt, @temp_hit, @temp_eval, @temp_len, @temp_qlen) = ();
        } 
        
        
        # Redundant check to make sure that the R_ sequence was found first.
        # If it was, It will store the length of the arrays it created in the %comp_storage hash
        # If not, it will set the length to -1
        my $_temp_cnt;
        if($comp_storage{R}){
            $_temp_cnt = scalar(@{$comp_storage{R}->[0]}) - 1;
        } else {
           $_temp_cnt = -1;
        }
        
        #---------------------------F_1 Sequence-------------------------------------------------
        #----------------------------------------------------------------------------------------
        #Sets the default flags for the retrieved sequences
        my $_f1_rank_flag = -1;
        my $_r1_rank_flag = -1;
        
        #Makes sure there are elements in the array for %comp_storage
        unless($_temp_cnt == -1){
            for(my $i = 0; $i <= $_temp_cnt; $i++){
                unless($_contig_retrieval{$temp_query}{F_1}->[7]){
                    $_f1_rank_flag = 4;
                    last;
                }
                my $_qlength_per = ($_contig_retrieval{$temp_query}{F_1}->[7] / $_contig_retrieval{$temp_query}{F_1}->[6]);
                #--- F_1 Hit match :COMPARE TO: Array of R_ List 
                #--- Hit Match is the same and above a significant length percentage
                # Makes sure the following conditions are met:
                #   1. F_1 is the same contig sequence as that retrieved from the R_ list
                #   2. F_1 Ratio of HSP length to End_Tag Length is above a Significant Level
                #   3. R_ Ratio of HSP length to End_Tag Length is above a Significant Level
                if ((($_contig_retrieval{$temp_query}{F_1}->[1]) eq ($comp_storage{R}->[1]->[$i])) && ($_qlength_per > $sig_level) && ((($comp_storage{R}->[3]->[$i]) / ($comp_storage{R}->[4]->[$i])) > $sig_level)) {
                    # Marks the flag as a Significant match
                    $_f1_rank_flag = 1;
                    push(@flag_storage, $comp_storage{R}->[0]->[$i]);
                    # Checks the rest of the R_ array for other potential matches
                    for(my $k = 0; $k <= $_temp_cnt; $k++){
                        my $_comp_len = ($comp_storage{R}->[3]->[$k]) / ($comp_storage{R}->[4]->[$k]);
                        if ($_comp_len > $sig_level) {
                            unless (grep{$_ eq ($comp_storage{R}->[0]->[$k])} @flag_storage) {
                                # Marks all the flags as AMBIGUOUS
                                $_f1_rank_flag = 3;
                                $_r1_rank_flag = 3;
                                push(@flag_storage, $comp_storage{R}->[0]->[$k]); #################
                            }  
                        }
                    }  #--- No Hit Match : Based off of length
                    #Repeat the process with the same conditions except:
                    #   1. F_1 is NOT the same contig sequence as that retrieved from the R_ list
                } elsif (($_qlength_per > $sig_level) && ((($comp_storage{R}->[3]->[$i]) / ($comp_storage{R}->[4]->[$i])) > $sig_level)){
                    #Mark as Significant +nonmatch
                    $_f1_rank_flag = 2;
                    push(@flag_storage, $comp_storage{R}->[0]->[$i]);
                    for(my $k = 0; $k <= $_temp_cnt; $k++){
                        my $_comp_len = ($comp_storage{R}->[3]->[$k]) / ($comp_storage{R}->[4]->[$k]);
                        if ($_comp_len > $sig_level ) {
                            # Checks the rest of the R_ array for other potential matches
                            unless (grep{$_ eq ($comp_storage{R}->[0]->[$k])} @flag_storage) {
                                $_f1_rank_flag = 3;
                                $_r1_rank_flag = 3;
                                push(@flag_storage, $comp_storage{R}->[0]->[$k]);
                            }  
                        }
                    }
                }
            }
        }
        
        #---------------------------R_1 Sequence-------------------------------------------------
        #----------------------------------------------------------------------------------------
        
        my $_temp_cnt_f;
        if($comp_storage{F}){
            $_temp_cnt_f = scalar(@{$comp_storage{F}->[0]}) - 1;
        } else {
            $_temp_cnt_f = -1;
        }
        unless($_temp_cnt_f == -1){
            for(my $i = 0; $i <= $_temp_cnt_f; $i++){
                unless($_contig_retrieval{$temp_query}{R_1}->[7]){
                    $_r1_rank_flag = 4;
                    last;
                }
                my $_qlength_per = ($_contig_retrieval{$temp_query}{R_1}->[7] / $_contig_retrieval{$temp_query}{R_1}->[6]);
                #--- R_1 Hit match :COMPARE TO: Array of F_ List
                #--- Hit Match is the same and above a significant length percentage
                if ((($_contig_retrieval{$temp_query}{R_1}->[1]) eq ($comp_storage{F}->[1]->[$i])) && ($_qlength_per > $sig_level) && ((($comp_storage{F}->[3]->[$i]) / ($comp_storage{F}->[4]->[$i])) > $sig_level)) {
                    $_r1_rank_flag = 1;
                    push(@flag_storage, $comp_storage{F}->[0]->[$i]);
                    for(my $k = 0; $k <= $_temp_cnt_f; $k++){
                        my $_comp_len = ($comp_storage{F}->[3]->[$k]) / ($comp_storage{F}->[4]->[$k]);
                        if ($_comp_len > $sig_level) {
                            unless (grep{$_ eq ($comp_storage{F}->[0]->[$k])} @flag_storage) {
                                $_r1_rank_flag = 3;
                                $_f1_rank_flag = 3;
                                push(@flag_storage, $comp_storage{F}->[0]->[$k]); #################
                            }  
                        }
                    }  #--- No Hit Match : Based off of length
                } elsif (($_qlength_per > $sig_level) && ((($comp_storage{F}->[3]->[$i]) / ($comp_storage{F}->[4]->[$i])) > $sig_level)){
                    $_r1_rank_flag = 2;####
                    push(@flag_storage, $comp_storage{F}->[0]->[$i]);
                    for(my $k = 0; $k <= $_temp_cnt_f; $k++){
                        my $_comp_len = ($comp_storage{F}->[3]->[$k]) / ($comp_storage{F}->[4]->[$k]);
                        if ($_comp_len > $sig_level ) {
                            unless (grep{$_ eq ($comp_storage{F}->[0]->[$k])} @flag_storage) {
                                $_r1_rank_flag = 3;
                                $_f1_rank_flag = 3;
                                push(@flag_storage, $comp_storage{F}->[0]->[$k]);
                            }  
                        }
                    }
                } 
            }
        }
        #@flag_storage = ();
        
        
    #--------------------------------------------------------------------------
    #---------------------------WRITING RESULTS--------------------------------
    #--------------------------------------------------------------------------
        
        
        foreach my $temp_rf(sort keys($_contig_retrieval{$temp_query})){
            my $s = substr($temp_rf, 0,1);
            
            if ((substr($temp_rf, 0,1)) =~ /F/) {
                if (grep{$_ eq $temp_rf} @flag_storage) {
                    writeContigFasta($_contig_retrieval{$temp_query}{$temp_rf}->[1], $_contig_retrieval{$temp_query}{$temp_rf}->[13]);
                    $_contig_retrieval{$temp_query}{$temp_rf}->[15] = $_f1_rank_flag;
                    my $stripped_name;
                    if ($_contig_retrieval{$temp_query}{$temp_rf}->[1] =~ /^(?:lcl\|)?(.+)$/) {
                         $stripped_name = $1;
                    }
                    print $_outcsv "$temp_query, $temp_rf, $stripped_name, $_contig_retrieval{$temp_query}{$temp_rf}->[2], $_contig_retrieval{$temp_query}{$temp_rf}->[3], $_contig_retrieval{$temp_query}{$temp_rf}->[4], $_contig_retrieval{$temp_query}{$temp_rf}->[5], $_contig_retrieval{$temp_query}{$temp_rf}->[6], $_contig_retrieval{$temp_query}{$temp_rf}->[7], $_contig_retrieval{$temp_query}{$temp_rf}->[8], $_contig_retrieval{$temp_query}{$temp_rf}->[10], $_contig_retrieval{$temp_query}{$temp_rf}->[11], length($_contig_retrieval{$temp_query}{$temp_rf}->[11]), $_contig_retrieval{$temp_query}{$temp_rf}->[15]\n";
                } else {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
                        $_f1_rank_flag = -1;
                        $_contig_retrieval{$temp_query}{$temp_rf}->[15] = $_f1_rank_flag;
                    }
                }
            } elsif ((substr($temp_rf, 0,1)) =~ /R/){
                if (grep{$_ eq $temp_rf} @flag_storage) {
                    writeContigFasta($_contig_retrieval{$temp_query}{$temp_rf}->[1], $_contig_retrieval{$temp_query}{$temp_rf}->[13]);
                    $_contig_retrieval{$temp_query}{$temp_rf}->[15] = $_r1_rank_flag;
                    my $stripped_name;
                    if ($_contig_retrieval{$temp_query}{$temp_rf}->[1] =~ /^(?:lcl\|)?(.+)$/) {
                         $stripped_name = $1;
                    }
                    print $_outcsv "$temp_query, $temp_rf, $stripped_name, $_contig_retrieval{$temp_query}{$temp_rf}->[2], $_contig_retrieval{$temp_query}{$temp_rf}->[3], $_contig_retrieval{$temp_query}{$temp_rf}->[4], $_contig_retrieval{$temp_query}{$temp_rf}->[5], $_contig_retrieval{$temp_query}{$temp_rf}->[6], $_contig_retrieval{$temp_query}{$temp_rf}->[7], $_contig_retrieval{$temp_query}{$temp_rf}->[8], $_contig_retrieval{$temp_query}{$temp_rf}->[10], $_contig_retrieval{$temp_query}{$temp_rf}->[11], length($_contig_retrieval{$temp_query}{$temp_rf}->[11]), $_contig_retrieval{$temp_query}{$temp_rf}->[15]\n";
                } else {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
                        $_r1_rank_flag = -1;
                        $_contig_retrieval{$temp_query}{$temp_rf}->[1] = $_r1_rank_flag;
                    }
                }
            }
        }
        @flag_storage = ();
        delete $comp_storage{'R'};
        delete $comp_storage{'F'};
    }
    system("rm -rf .temp/storage/write*");
    store (\%contig_orf, "temp/storage/contig.$$") or die "Could not store \%contig_orf\n";
    store (\%_contig_retrieval, "temp/storage/write.$$") or die "could not store";
    print $$;
}

sub writeContigFasta{
    my ($scaf_name, $scaf_seq) = @_;
    if ($scaf_name =~ /^(?:lcl\|)?(.+)$/) {
        $scaf_name = $1;
    }
    unless(exists $contig_orf{$scaf_name}){
        $scaf_seq =~ s/(.{1,80})/$1\n/gs;
        $contig_orf{$scaf_name} = [$scaf_seq,       #0 Contig Sequence
                                   {                #1  Gene Annotations
                                            'glimmer'   => {},
                                            'genbank'   => {},
                                            'manual'    => {}
                                   }];
        my $filename = 'temp/data/' . $scaf_name . '.fa';
        open(my $out_file, ">", $filename) or die "Could not create $filename : $!\n";
        print $out_file '>' . $scaf_name . "\n";
        print $out_file $scaf_seq . "\n";
        close $out_file
    }
}
__END__
    #--------------------------------------------------------------------------
    #---------------------------WRITING RESULTS--------------------------------
    #--------------------------------------------------------------------------
        
        

        foreach my $temp_rf(sort keys($_contig_retrieval{$temp_query})){
            if ((substr($temp_rf, 0,1)) =~ /F/) {
                if (grep{$_ eq $temp_rf} @flag_storage) {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
                        $_contig_retrieval{$temp_query}{$temp_query}->[15] = $_f1_rank_flag;
                        ($col_count == 0) ? (print $_outcsv $_f1_rank_flag . "," . $temp_query . "-" . $retrieved_element) : (print $_outcsv "," . $retrieved_element);
                        ($retrieved_element = $temp_query . "-" . $retrieved_element) if ($col_count == 0);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_ambg) if ($_f1_rank_flag == 3);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_fmatched_hit) if ($_f1_rank_flag == 1);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_fnonmatched_hit) if ($_f1_rank_flag == 2);
                        #$worksheet->write($row_count, $col_count, $retrieved_element, $format_f) if ($_f1_rank_flag == -1);
                        $col_count++;
                    }
                    if ($_f1_rank_flag != 3) {
                        store (\@{$_graphic_output{$temp_query}{$temp_rf}{'start'}}, "storage/start.$$") or die "could not store";
                        store (\@{$_graphic_output{$temp_query}{$temp_rf}{'end'}}, "storage/end.$$") or die "could not store";
                        store (\@{$_graphic_output{$temp_query}{$temp_rf}{'annotation'}}, "storage/annotation.$$") or die "could not store";
                        my $contig_len = length($_contig_retrieval{$temp_query}{$temp_rf}->[13]);
                        $_contig_retrieval{$temp_query}{$temp_rf}->[1] =~ /lcl\|(.+)/;
                        my $contig_name = $1 . "-F" . $_f1_rank_flag;
                        print "Line 548: \$contig_len - ($contig_len)  ||  \$contig_name - ($contig_name)\n";
                        system("perl BioGraphics.pl $$ $contig_len $contig_name");   
                    }
                } else {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
                        $_f1_rank_flag = -1;
                        $_contig_retrieval{$temp_query}{$temp_query}->[15] = $_f1_rank_flag;
                        ($col_count == 0) ? (print $_outcsv $_f1_rank_flag . "," . $temp_query . "-" . $retrieved_element) : (print $_outcsv "," . $retrieved_element);
                        ($retrieved_element = $temp_query . "-" . $retrieved_element) if ($col_count == 0);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_f);
                        $col_count++;
                    }
                }
            } elsif ((substr($temp_rf, 0,1)) =~ /R/){
                if (grep{$_ eq $temp_rf} @flag_storage) {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
                        $_contig_retrieval{$temp_query}{$temp_query}->[15] = $_r1_rank_flag;
                        ($col_count == 0) ? (print $_outcsv $_r1_rank_flag . "," . $temp_query . "-" . $retrieved_element) : (print $_outcsv "," . $retrieved_element);
                        ($retrieved_element = $temp_query . "-" . $retrieved_element) if ($col_count == 0);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_ambg) if ($_r1_rank_flag == 3);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_rmatched_hit) if ($_r1_rank_flag == 1);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_rnonmatched_hit) if ($_r1_rank_flag == 2);
                        $col_count++;
                    }
                    if ($_f1_rank_flag != 3) {
                        store (\@{$_graphic_output{$temp_query}{$temp_rf}{'start'}}, "storage/start.$$") or die "could not store";
                        store (\@{$_graphic_output{$temp_query}{$temp_rf}{'end'}}, "storage/end.$$") or die "could not store";
                        store (\@{$_graphic_output{$temp_query}{$temp_rf}{'annotation'}}, "storage/annotation.$$") or die "could not store";
                        my $contig_len = length($_contig_retrieval{$temp_query}{$temp_rf}->[13]);
                        $_contig_retrieval{$temp_query}{$temp_rf}->[1] =~ /lcl\|(.+)/;
                        my $contig_name = $1 . "-R" . $_f1_rank_flag;
                        print "Line 548: \$contig_len - ($contig_len)  ||  \$contig_name - ($contig_name)\n";
                        system("perl BioGraphics.pl $$ $contig_len $contig_name");
                        system("rm -rf ./storage/*");
                    }
                } else {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
                        $_r1_rank_flag = -1;
                        $_contig_retrieval{$temp_query}{$temp_query}->[15] = $_r1_rank_flag;
                        ($col_count == 0) ? (print $_outcsv $_r1_rank_flag . "," . $temp_query . "-" . $retrieved_element) : (print $_outcsv "," . $retrieved_element);
                        ($retrieved_element = $temp_query . "-" . $retrieved_element) if ($col_count == 0);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_r);
                        $col_count++;
                    }
                }
            }
            $row_count++;
            print $_outcsv "\n";
            $col_count = 0;
        }
        $row_count++;
        @flag_storage = ();
    }
    system("rm DBD*");
    system("rm _temp*");
    system("rm testdb*");
    store (\%_contig_retrieval, "storage/write.$$") or die "could not store";
}