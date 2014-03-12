#!/usr/bin/perl
use warnings;
use strict;
BEGIN {
    $ENV{BLASTPLUSDIR} = '/home/rene/endtags/end/install/ncbi-blast-2.2.29+-src/c++/ReleaseMT/bin';
    $ENV{PATH} .= ':/usr/bin/emboss/emboss';
}
use lib '/usr/bin/emboss/emboss';
use lib '/usr/lib/cpan/build/';
use lib '/usr/lib/cpan/build/BioPerl/lib';
use lib '/usr/lib/cpan/build/BioPerlEmboss/lib/';
use lib '/usr/lib/cpan/build/Storable/blib/lib';
use Bio::Seq;
use Bio::Tools::Run::StandAloneBlastPlus;
use Spreadsheet::ParseExcel;
use Spreadsheet::WriteExcel;
use Bio::AlignIO;
use Bio::SearchIO;
use Bio::SeqIO;
use Bio::Factory::EMBOSS;
use Data::Dumper;
use File::Path qw/make_path remove_tree/;
use Storable;
#$" = "\n";


#-----------------------------------------------------------------------#
#                                                                       #
#                       Set Parameters                                  #
#                                                                       #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                   Worksheet Colours                                   #
#-----------------------------------------------------------------------#
my $label_cell_color = 'aqua';          # Label cell colour
my $f_cell_color = 'aqua';              # Standard F_ cell colour
my $r_cell_color = 'yellow';            # Standard R_ cell colour
my $match_cell_color = 'aqua';          # Matched Contig cell colour
my $ambig_cell_color = 'yellow';        # Ambiguous Results cell colour 
#-----------------------------------------------------------------------#
#                   Misc. Parameters                                    #
#-----------------------------------------------------------------------#
my $limit = 30;                          # Minimum align sequence size
my $out_spreadsheet = 'matched.xls';    # Report .xls name
my $for_id = 'm13f';                    # Forward end tag name
my $rev_id = 'm13r';                    # Reverse end tag name
my $query_name = 'testquery';           # Query name
#-----------------------------------------------------------------------#
#                   BLAST Parameters                                    #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                   EMBOSS ORF Finder Parameters                        #
#-----------------------------------------------------------------------#
my $_database_type = "refseq_protein";
my $_local_remote = "remote";
my $output_orfs = "orfs2.fa";
my $_min_size = 30;                     # Default is 30 bp / 10 aa
my $_max_size = 1000000;                # Default : 1000000 bp
my $_output_format = 3;                 # Default = 3
    #0 : Translation of regions between STOP codons
    #1 : Translation of regions between START and STOP codons
    #2 : Nucleic sequences between STOP codons
    #3 : Nucleic sequences between START and STOP codons
    #4 : Nucleotides flanking START codons
    #5 : Nucleotides flanking initial STOP codons
    #6 : Nucleotides flanking ending STOP codons
my $_organism_code = 0;                # Default = 0
    #0      (Standard)
    #1 	    (Standard (with alternative initiation codons))
    #2 	    (Vertebrate Mitochondrial)
    #3 	    (Yeast Mitochondrial)
    #4 	    (Mold, Protozoan, Coelenterate Mitochondrial and Mycoplasma/Spiroplasma)
    #5 	    (Invertebrate Mitochondrial)
    #6 	    (Ciliate Macronuclear and Dasycladacean)
    #9 	    (Echinoderm Mitochondrial)
    #10     (Euplotid Nuclear)
    #11     (Bacterial)
    #12     (Alternative Yeast Nuclear)
    #13     (Ascidian Mitochondrial)
    #14     (Flatworm Mitochondrial)
    #15     (Blepharisma Macronuclear)
    #16     (Chlorophycean Mitochondrial)
    #21     (Trematode Mitochondrial)
    #22     (Scenedesmus obliquus)
    #23     (Thraustochytrium Mitochondrial)
my $_is_circular = "No";               # Default = No
my $_spurious_length = 100;
my $_annotation_switch = "OFF";         # Default = ON
#-----------------------------------------------------------------------#
#                   Spreadsheet Parameters                              #
#-----------------------------------------------------------------------#
my $write_workbook = Spreadsheet::WriteExcel->new($out_spreadsheet);
my $worksheet = $write_workbook->add_worksheet();
my $sig_level = 0.65;                    # Significant Hit/Query Length
my $spurious_level = 0.2;
my $_min_len_per = 0.7;                 # Query length percent - $_min_len_per
$write_workbook->set_custom_color(39, '#a7a7a7');   # Labels
#FORWARD
$write_workbook->set_custom_color(40, '#CCFFFF');   # Forward
$write_workbook->set_custom_color(45, '#99FF66');   # Matched Hit
$write_workbook->set_custom_color(46, '#FFFF99');   # Nonmatched Hit

#REVERSE
$write_workbook->set_custom_color(41, '#33FFFF');   # Reverse
$write_workbook->set_custom_color(42, '#00FF00');   # Matched Hit
$write_workbook->set_custom_color(43, '#FFFF33');   # Nonmatched Hit
$write_workbook->set_custom_color(44, '#ed495d');   # Ambiguous


#-----------------------------------------------------------------------#
#                   Private Variables                                   #
#-----------------------------------------------------------------------#
my $row_count = 0;
my $_temp_contig = "_tempcontig.fa";
my $_temp_orf_file = "_temporf.fa";
my $_query_length;
my $_query_name;
my $_hit_name;
my $_algorithm;
my $_evalue;
my $_per_identity;
my $_num_identity;
my $_hsp_length;
my @_query_range;
my @_hit_range;
my $_homology_str;                      # Currently set to Hit String
my %_contig_retrieval;
my %_graphic_output;
my $_rank_flag = -1;
open(my $_outcsv, "+>>", "data/_temp_data.csv") or die "Could not export to CSV file, $!\n";
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#

my %end_tag_seq;
print @ARGV;
if(scalar(@ARGV) != 3){
    print @ARGV, "\n";
    print "Endtag_F, Endtag_R and Databse required\n";
}   else {
# Assumes:
# ARGV[0] = End tag F CSV file
# ARGV[0] = End tag R CSV file
# ARGV[2] = Sequence file
my $end_tag_f_file = shift;
my $end_tag_r_file = shift;
my $seq_file = shift;

#Current segment is TEMPORARY:
# Parses an Excel file containing all the End Tag unique ID's and stores them in a hash
# with ID as a key pointing to an array containing F_ sequence and R_ sequence
#
# This area will be overwritten with extraction of the information from the database
# to generate the same type of has with End Tag Unique ID key pointing to the F_ and
# R_ Sequences

    open(my $f_file, "<", $end_tag_f_file) or die "No! $!\n";
    my @f_seqs = <$f_file>;
    open(my $r_file, "<", $end_tag_r_file) or die "No! $!\n";
    my @r_seqs = <$r_file>;
    
    foreach my $line(@f_seqs){
        chomp($line);
        my @temp_array_f = split(',', $line);
        foreach my $line_r(@r_seqs){
            chomp($line_r);
            if ($line_r =~ /$temp_array_f[0]/) {
                my @temp_array_r = split(',', $line_r);
                $end_tag_seq{$temp_array_f[0]} = [$temp_array_f[2], $temp_array_r[2]];
            }
        }
    }

    
    #---------------------------------------------------------------------------
    #                           BLAST
    #---------------------------------------------------------------------------
    # This area is intended to BLAST the end-tag F_ and R_ sequences for each unique ID to the
    # local specified database.  The local database will be inputted as a Fasta format file
    # under the variable $seq_file.
    #
    # Currently, the $seq_file is specified as a preexisting fasta format file in the current
    # working directory.  This will be overwritten as a dynamically generated Fasta File that
    # originates from the associated "Pooled" data in the database.
    
    #Creates the BLAST object using the local fasta database
    my $blast_obj = Bio::Tools::Run::StandAloneBlastPlus->new(
                                            -db_name => 'testdb',
                                            -db_data => $seq_file,
                                            -create => 1);
    
    # Makes a temporary directory for each End-Tag Unique ID
    # Creates a Seq object containing the F_ or R_ sequence for that end-tag sequence
    # BLASTs the sequences against the fasta database and stores the related BLAST information
    # in the appropriate folder.
    foreach(keys(%end_tag_seq)){
        make_path("temp/$_");
        #-------------------LOCAL BLAST CONTIG RETRIEVAL------------------------
        foreach my $for_rev(0..1){
            my $seq_obj = Bio::Seq->new(
                                -id => $query_name,
                                -seq => $end_tag_seq{$_}->[$for_rev]
                                );
            my($for_rev_name, $f_r);
            ($for_rev == 0) ? ($f_r = "F_") : ($f_r = "R_");
            ($for_rev == 0) ? ($for_rev_name = "Forward.txt") : ($for_rev_name = "Reverse.txt");
            
            # Executes a blastn search using the sequence on the database
            my $result = $blast_obj->blastn(
                                -query => $seq_obj,
                                -outfile => "temp/$_/$for_rev_name");

            print "*" x 50, "\n";
            print "End Tag Sequence: ", $_, "\n";
            print "Number of hits: ", $result->num_hits(), "\n";
            
            
            #Parse the newly created BLAST file 
            my $in_f = Bio::SearchIO->new(
                                        -format => 'blast',
                                        -file => "temp/$_/$for_rev_name");
            
            #For each Result, each hit, each hsp, retrieve the following information and store
            # it into a hash of the End Tag Unique ID which points to a count of the HSPs being
            # reported on, which points to an array containing all relevant information
            #   Refer to the comments below for retrieved data.  
            while(my $result = $in_f->next_result()){
                my $count = 0;
                $_query_length = $result->query_length();
                while(my $hit = $result->next_hit()){
                    while(my $hsp = $hit->next_hsp()){
                        if($hsp->length('total') > $limit){
                            my $num = $f_r . ++$count;
                            $_query_name = $_;
                            $_hit_name = $hit->name();
                            $_algorithm = $hit->algorithm();
                            $_evalue = $hsp->evalue();
                            $_per_identity = $hsp->percent_identity();
                            $_num_identity = $hsp->num_identical();
                            $_hsp_length = $hsp->hsp_length();
                            @_query_range = $hsp->range('query'); 
                            @_hit_range = $hsp->range('hit'); 
                            $_homology_str = $hsp->hit_string();
                            
                            my $scaffold_seq;
                            my $scaffold_obj = Bio::SeqIO->new(
                                                            -format => 'fasta',
                                                            -file => "$seq_file",);
                            while (my $_scaff_seq = $scaffold_obj->next_seq()) {
                                if (($_scaff_seq->id()) =~ /$_hit_name$/) {
                                    $scaffold_seq = $_scaff_seq->seq();
                                    last;
                                } 
                            }

                            $_contig_retrieval{$_query_name}{$num} =
                                        [
                                         $num,              #e.g. F_1
                                         $_hit_name,        # Hit name      i.e. lsl|scaffold751_3
                                         $_algorithm,       # Algorithm     i.e. blastn
                                         $_evalue,          # Blast e-value
                                         $_per_identity,    # Percent identity
                                         $_num_identity,    # Number of identical residues
                                         $_query_length,    # Length of the end-tag query sequence
                                         $_hsp_length,      # HSP length
                                         $_query_range[0],  # Start - HSP aligned to the query sequence
                                         $_query_range[1],  # End - HSP aligned to the query sequence
                                         $_hit_range[0],    # Start - HSP aligned to the contig sequence
                                         $_hit_range[1],    # End - HSP aligned to the contig sequence
                                         $_homology_str,    # Hit-string on the contig sequence
                                         $scaffold_seq      # Complete sequence of the contig (i.e. lsl|scaffold751_3)
                                        ];
                        } 
                    }
                }
            }
        } 
    }
    $blast_obj->cleanup();
    
    #---------------------------------------------------------------------------
    #                           EMBOSS ORF Finder
    #---------------------------------------------------------------------------
    # ORF Annotation:
    #  EXTREMELY likely to be deleted and exported to using Glimmer-MG
    #  No comments will be made until final decision has been made.
    
    my $orf_factory = Bio::Factory::EMBOSS->new();
    foreach my $temp_query(keys(%_contig_retrieval)){
        foreach my $temp_rf(keys($_contig_retrieval{$temp_query})){
            if($_contig_retrieval{$temp_query}{$temp_rf}->[7] > $_spurious_length){
                print $_contig_retrieval{$temp_query}{$temp_rf}->[7], " -$_spurious_length --- ", $_contig_retrieval{$temp_query}{$temp_rf}->[1], " --- ", "$temp_query. $temp_rf --- \n";
                my $_list_end = scalar(@{$_contig_retrieval{$temp_query}{$temp_rf}});
                my $contig_seq = $_contig_retrieval{$temp_query}{$temp_rf}->[13];
                my $contig_obj = Bio::Seq->new(
                                                -seq => "$contig_seq",
                                                -display_id => "$temp_query:$temp_rf",
                                                );
                my $temp_contig  = Bio::SeqIO->new(
                                                -file => ">$_temp_contig",
                                                -format => "fasta",
                                                );
                $temp_contig->write_seq($contig_obj);
                my %input = (
                            -sequence => "$_temp_contig",
                            -minsize => $_min_size,
                            -maxsize => $_max_size,
                            -outseq => "$output_orfs",
                            -table => $_organism_code,
                            -find => $_output_format,
                            -circular => "$_is_circular",
                            -methionine => "N");
                my $orf_app = $orf_factory->program("getorf");
                my $result = $orf_app->run(\%input);
               
                my $inorf = Bio::SeqIO->new(
                                           -format => 'fasta',
                                           -file => "$output_orfs",
                                           );
                $_graphic_output{$temp_query}{$temp_rf}{'start'} = [];
                $_graphic_output{$temp_query}{$temp_rf}{'end'} = [];
                $_graphic_output{$temp_query}{$temp_rf}{'start'} = [];
                
                while (my $_orf_seq = $inorf->next_seq()) {
                    my $temp_orf_seq = $_orf_seq->seq();
                    my $temp_orf_loc = $_orf_seq->desc();
                    my ($start, $end);
                    if($temp_orf_loc =~ /^\[(\d+?)\s+?-\s+?(\d+?)\]\s*?$/){
                        $start = $1;
                        $end = $2;
                    } else {                                         # IGnores the Reverse Sense strand
                        last;
                    }
                    #print "Line 278: \$temp_orf_loc is $temp_orf_loc -- $start - $end\n";
                    push($_contig_retrieval{$temp_query}{$temp_rf}, $temp_orf_seq);
                    push($_contig_retrieval{$temp_query}{$temp_rf}, $start);
                    push($_contig_retrieval{$temp_query}{$temp_rf}, $end);
                    push($_graphic_output{$temp_query}{$temp_rf}{'start'}, $start);
                    push($_graphic_output{$temp_query}{$temp_rf}{'end'}, $end);
                    #print "Line 271: \$temp_orf_seq - $temp_orf_seq\n";
                    
                    
                    if ($_annotation_switch eq "ON") {
                        my $blast_orf_obj = Bio::Tools::Run::StandAloneBlastPlus->new(
                                                                                    -db_name => "$_database_type",
                                                                                    -remote => 'remote',
                                                                                    #-DB_DIR => '/home/rene/endtags/end/install/ncbi-blast-2.2.29+-src/db',
                                                                                    );
                        
                        
                        my $seq_orf_obj = Bio::Seq->new(
                                                        -id => "orf",
                                                        -seq => "$temp_orf_seq",
                                                        );
                        print "Sequence: $temp_orf_seq\n";
                        print "Starting BlastX Query....\n";
                        my $orf_result = $blast_orf_obj->blastx(
                                                                -query => $seq_orf_obj,
                                                                -outfile => "$_temp_orf_file",
                                                                );
                        print "Blasting the query is complete.\n";
                        my $orf_in = Bio::SearchIO->new(
                                                        -format => 'blast',
                                                        -file => "$_temp_orf_file",
                                                        );
                        my $result = $orf_in->next_result();
                        print "Line 297: $result\n";
                        if(my $hit = $result->next_hit()){
                            print "Line 273: Here\n";
                            my $_annotation = $hit->description();
                            my $_annotation2 = $hit->name() . " " . $hit->description() . " " . $hit->locus();
                            push($_contig_retrieval{$temp_query}{$temp_rf}, $_annotation);
                            print Dumper(\%_contig_retrieval);
                            print "Hit Name: ", $hit->name(), "---- Description: ", $hit->description(), "\n";
                            print "Name [14]: ", $_contig_retrieval{$temp_query}{$temp_rf}->[14], " ---- Sequence: ", $_contig_retrieval{$temp_query}{$temp_rf}->[13], "\n";
                            print "Name [16]: ", $_contig_retrieval{$temp_query}{$temp_rf}->[16], " ---- Sequence: ", $_contig_retrieval{$temp_query}{$temp_rf}->[15], "\n";
                        }    
                    } 
                }       
            }  
        }
    }
    
    #---------------------------------------------------------------------------
    #                           Spreadsheet
    #---------------------------------------------------------------------------
    #   Flag:   0 - Default
    #           -1 - Spurious
    #           1 - Significant - Matched Hit Seq
    #           2 - Significant - Nonmatched Hit Seq
    #           3 - Ambiguous
    #           4 - No Contig Hit
    my $format_title = $write_workbook->add_format(bg_color => 39);
    my $format_f = $write_workbook->add_format(bg_color => 40);
    my $format_r = $write_workbook->add_format(bg_color => 41);
    my $format_fmatched_hit = $write_workbook->add_format(bg_color => 45);
    my $format_fnonmatched_hit = $write_workbook->add_format(bg_color => 46);
    my $format_rmatched_hit = $write_workbook->add_format(bg_color => 42);
    my $format_rnonmatched_hit = $write_workbook->add_format(bg_color => 43);
    my $format_ambg = $write_workbook->add_format(bg_color => 44);
    my $col_count = 0;
    my @titles = qw/End_Tag Contig_Seq Algorithm E_Value %_Identity Num_Identity Endtag_Length HSP_Length Query_Start Query_End Contig_Start Contig_End Contig_Hit_Seq Contig_Seq ORF_Seq ORF_Annotation/;
        foreach my $label(@titles){
            $worksheet->write($row_count, $col_count, $label, $format_title);
            $col_count++;
        }
    $row_count++;
    $col_count = 0;
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
            print "\$temp_rf $temp_rf and \$_tf $_tf\n";
            if ($temp_rf =~/$_tf/) {
                $_tf = "F";
                $comp_storage{$_tf} = [[@temp_cnt], [@temp_hit], [@temp_eval], [@temp_len], [@temp_qlen]];
                (@temp_cnt, @temp_hit, @temp_eval, @temp_len, @temp_qlen) = ();
            }
            push(@temp_cnt, $temp_rf);
            push(@temp_hit, $_contig_retrieval{$temp_query}{$temp_rf}->[1]);
            push(@temp_eval, $_contig_retrieval{$temp_query}{$temp_rf}->[3]);
            push(@temp_len, $_contig_retrieval{$temp_query}{$temp_rf}->[7]);
            push(@temp_qlen, $_contig_retrieval{$temp_query}{$temp_rf}->[6]);
            print "-------------------- $_tf\n";
            
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
        print "Line 317: \$temp_query ===> $temp_query\n";
        my $_temp_cnt;
        if($comp_storage{R}){
            $_temp_cnt = scalar(@{$comp_storage{R}->[0]}) - 1;
        } else {
           $_temp_cnt = -1;
        }
        my $ambg_count = 0;     #ambg_count, 2 or more = multiple hits
        
        #---------------------------F_1 Sequence-------------------------------------------------
        #----------------------------------------------------------------------------------------
        
        #Sets the default flags for the retrieved sequences
        my $_f1_rank_flag = -1;
        my $_r_flag = 0;
        
        #Makes sure there are elements in the array for %comp_storage
        unless($_temp_cnt == -1){
            for(my $i = 0; $i <= $_temp_cnt; $i++){
                print "Line 386: $i and $_temp_cnt\n";
                unless($_contig_retrieval{$temp_query}{F_1}->[7]){
                    $_f1_rank_flag = 4;
                    last;
                }
                my $_qlength_per = ($_contig_retrieval{$temp_query}{F_1}->[7] / $_contig_retrieval{$temp_query}{F_1}->[6]);
                print "Line 369: ", $_contig_retrieval{$temp_query}{F_1}->[1], " ===$temp_query===> ", $comp_storage{R}->[1]->[$i], " : ", $comp_storage{R}->[0]->[$i], "\n";
                #--- F_1 Hit match :COMPARE TO: Array of R_ List 
                #--- Hit Match is the same and above a significant length percentage
                # Makes sure the following conditions are met:
                #   1. F_1 is the same contig sequence as that retrieved from the R_ list
                #   2. F_1 Ratio of HSP length to End_Tag Length is above a Significant Level
                #   3. R_ Ratio of HSP length to End_Tag Length is above a Significant Level
                if ((($_contig_retrieval{$temp_query}{F_1}->[1]) eq ($comp_storage{R}->[1]->[$i])) && ($_qlength_per > $sig_level) && ((($comp_storage{R}->[3]->[$i]) / ($comp_storage{R}->[4]->[$i])) > $sig_level)) {
                    # Marks the flag as a Significant +match
                    $_f1_rank_flag = 1;
                    $ambg_count++;
                    $_r_flag++;
                    push(@flag_storage, $comp_storage{R}->[0]->[$i]);
                    # Checks the rest of the R_ array for other potential matches
                    for(my $k = 0; $k <= $_temp_cnt; $k++){
                        my $_comp_len = ($comp_storage{R}->[3]->[$k]) / ($comp_storage{R}->[4]->[$k]);
                        if ($_comp_len > $sig_level) {
                            unless (grep{$_ eq ($comp_storage{R}->[0]->[$k])} @flag_storage) {
                                # Marks all the flags as AMBIGUOUS
                                $_f1_rank_flag = 3;
                                $_r_flag++;
                                $ambg_count++;
                                push(@flag_storage, $comp_storage{R}->[0]->[$k]); #################
                                print "Line 343: Unless Loop R - @flag_storage \n";
                            }  
                        }
                    }  #--- No Hit Match : Based off of length
                    #Repeat the process with the same conditions except:
                    #   1. F_1 is NOT the same contig sequence as that retrieved from the R_ list
                } elsif (($_qlength_per > $sig_level) && ((($comp_storage{R}->[3]->[$i]) / ($comp_storage{R}->[4]->[$i])) > $sig_level)){
                    #Mark as Significant +nonmatch
                    $_f1_rank_flag = 2;
                    $_r_flag++;
                    $ambg_count++;
                    push(@flag_storage, $comp_storage{R}->[0]->[$i]);
                    for(my $k = 0; $k <= $_temp_cnt; $k++){
                        my $_comp_len = ($comp_storage{R}->[3]->[$k]) / ($comp_storage{R}->[4]->[$k]);
                        if ($_comp_len > $sig_level ) {
                            # Checks the rest of the R_ array for other potential matches
                            unless (grep{$_ eq ($comp_storage{R}->[0]->[$k])} @flag_storage) {
                                print "Testing One: \$_ $_ ---", $comp_storage{R}->[0]->[$k], "\n";
                                $_f1_rank_flag = 3;
                                $_r_flag++;
                                $ambg_count++;
                                push(@flag_storage, $comp_storage{R}->[0]->[$k]);
                            }  
                        }
                    }
                } 
            }
        }
        print "Line 366: \@flag_storage After F_1: @flag_storage\n";
        
        #---------------------------R_1 Sequence-------------------------------------------------
        #----------------------------------------------------------------------------------------
        my $_r1_rank_flag = -1;
        my $_f_flag = 0;
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
                    $ambg_count++;
                    $_f_flag++;
                    push(@flag_storage, $comp_storage{F}->[0]->[$i]);
                    for(my $k = 0; $k <= $_temp_cnt_f; $k++){
                        my $_comp_len = ($comp_storage{F}->[3]->[$k]) / ($comp_storage{F}->[4]->[$k]);
                        if ($_comp_len > $sig_level) {
                            unless (grep{$_ eq ($comp_storage{F}->[0]->[$k])} @flag_storage) {
                                $_r1_rank_flag = 3;
                                $_f1_rank_flag = 3;
                                $_f_flag++;
                                $ambg_count++;
                                push(@flag_storage, $comp_storage{F}->[0]->[$k]); #################
                                print "Line 390: Unless Loop F - @flag_storage \n";
                            }  
                        }
                    }  #--- No Hit Match : Based off of length
                } elsif (($_qlength_per > $sig_level) && ((($comp_storage{F}->[3]->[$i]) / ($comp_storage{F}->[4]->[$i])) > $sig_level)){
                    $_r1_rank_flag = 2;####
                    $_f_flag++;
                    $ambg_count++;
                    push(@flag_storage, $comp_storage{F}->[0]->[$i]);
                    for(my $k = 0; $k <= $_temp_cnt_f; $k++){
                        my $_comp_len = ($comp_storage{F}->[3]->[$k]) / ($comp_storage{F}->[4]->[$k]);
                        if ($_comp_len > $sig_level ) {
                            unless (grep{$_ eq ($comp_storage{F}->[0]->[$k])} @flag_storage) {
                                print "Testing Three: \$_ $_ ---", $comp_storage{F}->[0]->[$k], "\n";
                                $_r1_rank_flag = 3;
                                $_f1_rank_flag = 3;
                                $_f_flag++;
                                $ambg_count++;
                                push(@flag_storage, $comp_storage{F}->[0]->[$k]);
                            }  
                        }
                    }
                } 
            }
        }
        print "Line 412: \@flag_storage After R_1: @flag_storage\n \t\t\t\t\t==> \$_f1_rank_flag : $_f1_rank_flag || \$_r1_rank_flag : $_r1_rank_flag\n";
        #@flag_storage = ();
        
        
    #--------------------------------------------------------------------------
    #---------------------------WRITING RESULTS--------------------------------
    #--------------------------------------------------------------------------
        
        

        foreach my $temp_rf(sort keys($_contig_retrieval{$temp_query})){
            if ((substr($temp_rf, 0,1)) =~ /F/) {
                if (grep{$_ eq $temp_rf} @flag_storage) {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
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
                        ($col_count == 0) ? (print $_outcsv $_f1_rank_flag . "," . $temp_query . "-" . $retrieved_element) : (print $_outcsv "," . $retrieved_element);
                        ($retrieved_element = $temp_query . "-" . $retrieved_element) if ($col_count == 0);
                        $worksheet->write($row_count, $col_count, $retrieved_element, $format_f);
                        $col_count++;
                    }
                }
            } elsif ((substr($temp_rf, 0,1)) =~ /R/){
                if (grep{$_ eq $temp_rf} @flag_storage) {
                    foreach my $retrieved_element(@{$_contig_retrieval{$temp_query}{$temp_rf}}){
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
    system("rm -rf _temp*");
    system("rm -rf testdb*");
    
}
__END__
=pod
my $parse = Spreadsheet::ParseExcel->new();
my $workbook = $parse->parse("$end_tag_file");

    for my $worksheet($workbook->worksheets()){
        my ($ID_col, $F_col, $R_col);
        my ($row_min, $row_max) = $worksheet->row_range();
        my ($col_min, $col_max) = $worksheet->col_range();
        for my $row($row_min..$row_max){#----------------------------------------------------------------------------------------------------
            my ($val, $ID_val, $F_val, $R_val);
            for my $col($col_min..$col_max){
                my $cell = $worksheet->get_cell($row, $col);
                my $val = $cell->value();
                if($val){
                $ID_col = $col if($val =~ /identifier/i);
                $F_col = $col if($val =~ /$for_id/i);
                $R_col = $col if($val =~ /$rev_id/i);
                $ID_val = $val if ($row >= 1 && $col == $ID_col);                
                $F_val = $val if ($row >= 1 && $col == $F_col);
                $R_val = $val if ($row >= 1 && $col == $R_col);
                };
            }
            $end_tag_seq{$ID_val} = [$F_val, $R_val] if ($F_val && $R_val && $ID_val);
        }
    }
=cut