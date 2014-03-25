#!/usr/bin/perl
use warnings;
use strict;
BEGIN {
    $ENV{BLASTPLUSDIR} = '/home/rene/endtags/end/install/ncbi-blast-2.2.29+-src/c++/ReleaseMT/bin';
    $ENV{PATH} .= ':/usr/bin/emboss/emboss';
}
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

my $parentid = $ARGV[0];
my $_contig_retrieval = retrieve("storage/write.$parentid") or die "Could not retrieve $!\n";
my %_contig_retrieval = %{$_contig_retrieval};
(system('rm -rf ./query.sh')) if (-e './query.sh');
open(my $mpi_bash, ">>", "./query.sh") or die "Could not create file\n";;
print $mpi_bash '#!/bin/bash', "\n";

#orf00045 386 -1 -2 52.14 I:272 D: S:
opendir(my $glimmer_predicts, "./predicts") or die "Could not open this folder\n";
my @files = grep{/.+?\.predict/} readdir($glimmer_predicts);
foreach my $predict_files(@files){
    if($predict_files =~ /^(.+?)\-\-(.+?)\.predict$/){
        my $_query_name = $1;
        my $num = $2;
        if (exists $_contig_retrieval{$_query_name}) {
            open(my $file, "<", "./predicts/$predict_files") or die "Could not open predict file, $!\n";
            open(my $blast_fa, ">>", "./orf_seq/" . $_query_name . '--' . $num . '.fa') or die "Could not create file\n";;
            foreach my $line (<$file>){
                chomp($line);
                if ($line =~ /^(orf\d*?)\s+?(\d+?)\s+?((?:-)?\d+?)\s+?((?:-)?\d+?)\s+?(\d+?\.\d+?)\s/) {
                    my $orf_id = $1;
                    my $rf = $4;
                    my $end;
                    my $start;
                    my $seq;
                    if ($rf > 0) {
                        $start = $2;
                        ($3 == -1) ? ($end = length($_contig_retrieval{$_query_name}{$num}->[13])) : ($end = $3);
                        $seq = substr($_contig_retrieval{$_query_name}{$num}->[13], $start, ($end-$start));
                    } else {
                        $end = $2;
                        ($3 == -1) ? ($start = 0) : ($start = $3);
                        $seq = substr($_contig_retrieval{$_query_name}{$num}->[13], $start, ($end-$start));
                        $seq =~ tr/ACGT/TGCA/;
                        $seq = reverse($seq);
                    }
                    my $score = $5;
                    $_contig_retrieval{$_query_name}{$num}->[14]{'glimmer'}{$orf_id} = {
                                                                             'start'    => $start,
                                                                             'end'      => $end,
                                                                             'reading_frame' => $rf,
                                                                             'score'    => $score,
                                                                             'annotation'   => '',
                                                                             'sequence'     => $seq
                                                                            };
                    print $blast_fa ">" . $orf_id, "\n";
                    print $blast_fa $seq, "\n\n";
                } 
            }
            print $mpi_bash 'mpiblast -d refseq -i ' .
                    $_query_name . '--' . $num .
                    ' -p blastn -o ' .
                    $_query_name . '--' . $num . '.out' .
                    ' --use-parallel-write --use-virtual-frags' . "\n";
        }
    }
}
store (\%_contig_retrieval, "storage/write.$$") or die "could not store";
print $$;


