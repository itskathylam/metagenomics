#!/usr/bin/perl
use warnings;
use strict;
BEGIN {
    $ENV{BLASTPLUSDIR} = '/home/rene/endtags/end/install/ncbi-blast-2.2.29+-src/c++/ReleaseMT/bin';
    $ENV{PATH} .= ':/usr/bin/emboss/emboss';
}
use lib '/usr/share/perl5';
#use lib '/usr/bin/emboss/emboss';
use lib '/usr/lib/cpan/custom/';
use lib '/usr/lib/cpan/custom/BioPerl';
use lib '/usr/lib/cpan/custom/BioPerl-SABP/lib/';
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
#$" = "\n";


#-----------------------------------------------------------------------#
#                                                                       #
#                       Set Parameters                                  #
#                                                                       #
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#
#                   Misc. Parameters                                    #
#-----------------------------------------------------------------------#
my $limit = 30;                          # Minimum align sequence size
my $query_name = 'testquery';           # Query name

#-----------------------------------------------------------------------#
#                   Private Variables                                   #
#-----------------------------------------------------------------------#
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
#-----------------------------------------------------------------------#
#-----------------------------------------------------------------------#

my %end_tag_seq;
#print @ARGV;
if(scalar(@ARGV) != 3){
    print @ARGV, "\n";
    print "Endtag_F, Endtag_R and Databse required\n";
}   else {
# Assumes:
# ARGV[0] = End tag F CSV file
# ARGV[1] = End tag R CSV file
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
        $line =~ s/\r//g;
        chomp($line);
        if ($line =~ /^[^(\s)]/){
            my @temp_array_f = split(',', $line);
            foreach my $line_r(@r_seqs){
                $line_r =~ s/\r//g;
                chomp($line_r);
                if ($line_r =~ /$temp_array_f[0]/) {
                    my @temp_array_r = split(',', $line_r);
                    $end_tag_seq{$temp_array_f[0]} = [$temp_array_f[2], $temp_array_r[2]];
                }
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

            #print "*" x 50, "\n";
            #print "End Tag Sequence: ", $_, "\n";
            #print "Number of hits: ", $result->num_hits(), "\n";
            
            
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
                                         $num,              #0   e.g. F_1
                                         $_hit_name,        #1   Hit name      i.e. lsl|scaffold751_3
                                         $_algorithm,       #2   Algorithm     i.e. blastn
                                         $_evalue,          #3   Blast e-value
                                         $_per_identity,    #4   Percent identity
                                         $_num_identity,    #5   Number of identical residues
                                         $_query_length,    #6   Length of the end-tag query sequence
                                         $_hsp_length,      #7   HSP length
                                         $_query_range[0],  #8   Start - HSP aligned to the query sequence
                                         $_query_range[1],  #9   End - HSP aligned to the query sequence
                                         $_hit_range[0],    #10  Start - HSP aligned to the contig sequence
                                         $_hit_range[1],    #11  End - HSP aligned to the contig sequence
                                         $_homology_str,    #12  Hit-string on the contig sequence
                                         $scaffold_seq,      #13  Complete sequence of the contig (i.e. lsl|scaffold751_3)
                                         {                  #14  Gene Annotations
                                            'consensus' => {},
                                            'glimmer'   => {},
                                            'genbank'   => {},
                                            'manual'    => {}
                                         },
                                         -1
                                        ];
                        } 
                    }
                }
            }
        } 
    }
    store (\%_contig_retrieval, "storage/write.$$") or die "could not store";
    print $$;
    $blast_obj->cleanup();
}

__END__ 
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
}