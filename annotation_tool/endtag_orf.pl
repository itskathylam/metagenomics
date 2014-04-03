#!/usr/bin/perl
use warnings;
use strict;
use lib '/usr/share/perl5';
use lib '/usr/bin/emboss/emboss';
use lib '/usr/lib/cpan/custom/';
use lib '/usr/lib/cpan/custom/BioPerl';
use lib '/usr/lib/cpan/custom/BioPerl-SABP/lib';
use lib '/usr/lib/cpan/custom/Storable/blib/lib';
use Bio::Seq;
use Bio::Tools::Run::StandAloneBlastPlus;
use Spreadsheet::ParseExcel;
use Spreadsheet::WriteExcel;
use Bio::AlignIO;
use Bio::SearchIO;
use Bio::SeqIO;
use Data::Dumper;
use File::Path qw/make_path remove_tree/;
use Storable;
use LWP::Simple;
use Cwd;

my $parentid = $ARGV[0];
my $cwd = $ARGV[1];
chdir("$cwd");

open(my $out2, ">>", "orf_pred_out.txt")or die "Can't export to orf_pred_out$!\n";


my $_contig_orf = retrieve("temp/storage/contig.$parentid") or die "Could not retrieve $!\n";
my %contig_orf = %{$_contig_orf};
(system('rm -rf ./query.sh')) if (-e './query.sh');
open(my $mpi_bash, ">>", "./temp/predicts/query.sh") or die "Could not create file\n";;
print $mpi_bash '#!/bin/bash', "\n";

opendir(my $glimmer_predicts, "./temp/predicts") or die "Could not open this folder\n";
my @files = grep{/(?:.+?\.out)|(?:.+?\.faa)|(?:.+?\.ffn)/} readdir($glimmer_predicts);
foreach my $predict_files(@files){
    if($predict_files =~ /^(.+?)\.out$/){
        my $scaffold = $1;
        if (exists $contig_orf{$scaffold}) {
                #Opens the predict .out file containing the location of the ORF file
            open(my $file, "<", "./temp/predicts/$predict_files") or die "Could not open predict file, $!\n";
            my $orf_cnt = 0;
            foreach my $line (<$file>){
                chomp($line);
                if ($line =~ /^(\d*?)\s+?(\d+?)\s+?([+-])\s+?([123])\s+?(.*?)\s/){
                    my $orf_id = $scaffold . '-' . ++$orf_cnt;
                    my $start = $1;
                    my $rf = $3 . $4;
                    my $end = $2;
                    my $score = $5;
                    
                    my $seq;
                    
                    open(my $contig_fh, "<", "temp/data/$scaffold.fa") or die "Could not open up contig file:$!\n";
                    my @contig_ar = <$contig_fh>;
                    chomp(@contig_ar);
                    my $contig_seq = join("", @contig_ar);
                    
                    my $seqin_o = Bio::SeqIO->new( -file => "<temp/predicts/$scaffold" . ".ffn",
                                                  -format => 'fasta');
                    while (my $seq_o = $seqin_o->next_seq()) {
                        my $header = $seq_o->display_id();
                        if ($header =~ /$scaffold\_(\d+?)_(\d+?)_/){
                            my ($s, $e) = ($1, $2);
                            if (($s == $start) && ($e == $end)) {
                                $seq = $seq_o->seq();
                            } elsif ($s == $start || $e == $end){ #TEMPORARY FIX
                                $start = $s;
                                $end = $e;
                                $seq = $seq_o->seq();
                            }              # DELETE UP TO HERE
                            print $out2 "-----------------------------------------------\n";
                            #$contig_seq =~ /((?<=(.{3}))$seq)/;
                            #$seq = $2 . $1;
                            #print $out2 "\$2 is: $seq || \$1 is: $1\n\$seq is: $seq\n";
                        }
                    }
                    close($contig_fh);
                    
                    $contig_orf{$scaffold}->[1]{'glimmer'}{$orf_id} = {
                                                                             'start'    => $start,
                                                                             'end'      => $end,
                                                                             'reading_frame' => $rf,
                                                                             'score'    => $score,
                                                                             'annotation'   => '',
                                                                             'sequence'     => $seq
                                                                            };
                } 
            }
        }
    }
}
store (\%contig_orf, "temp/storage/contig.$$") or die "could not store";
print $$;


