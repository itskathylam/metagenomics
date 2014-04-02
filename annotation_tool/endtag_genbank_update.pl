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
use Bio::AlignIO;
use Bio::SearchIO;
use Bio::SeqIO;
use Data::Dumper;
use File::Path qw/make_path remove_tree/;
use Storable;
use LWP::Simple;
use Cwd;

if (scalar(@ARGV) == 2) {
    my $parentid = $ARGV[0];
    my $cwd = $ARGV[1];
    chdir("$cwd");
    my $_contig_orf = retrieve("temp/storage/contig.$parentid") or die "Could not retrieve $!\n";
    my %contig_orf = %{$_contig_orf};
    my %parse_blast;
    my %acc_arr;
    
    foreach my $scaf(keys %contig_orf){
        if ($contig_orf{$scaf}->[2]) {
            my $acc = $contig_orf{$scaf}->[2];
            $acc_arr{$scaf} = $acc;
        } else {
            $acc_arr{$scaf} = 'HE798385.1';
        }
    }
    #Retrieves the genbank files in batch
    getGenbank(\%acc_arr);
    

    opendir(my $genbank_fh, "./temp/genbank") or die "Could not open this folder\n";
    my @genbank_files = grep{/.+?\.gbk/} readdir($genbank_fh);
    foreach my $gbk_f(@genbank_files){
        if ($gbk_f =~ /^(.+?)\.gbk/) {
            my $scaffold = $1;
            # Opens each retrieved genbank file and parses it:
            my $seqio_o = Bio::SeqIO->new(-file => "temp/genbank/$gbk_f",
                                          -format => 'genbank');
            my $seq_o = $seqio_o->next_seq();
            
            # BLASTs the contig sequence against the sequence obtained from the genbank file for that sequence
            my $query_seq_o = Bio::Seq->new(-id => $scaffold,
                                            -seq => $contig_orf{$scaffold}->[0]);
            my $blast_o = Bio::Tools::Run::StandAloneBlastPlus->new(-db_name => 'testdb',
                                                                    -create => 1);
            $blast_o->bl2seq(-method    => 'blastn',
                             -query     => $query_seq_o,
                             -subject   => $seq_o,
                             -outfile => "temp/data/blast/$scaffold.blast");
            $blast_o->cleanup();
            
            #Analyzes the BLAST result for the contig sequence alignment against the genbank file:
            my ($acc, $start_end_r, $start_orf_r, $end_orf_r) = parseBLAST($scaffold);
            $parse_blast{$scaffold}{'start'} = $start_orf_r;
            $parse_blast{$scaffold}{'end'} = $end_orf_r;
            $parse_blast{$scaffold}{'align'} = $start_end_r;
            $parse_blast{$scaffold}{'acc_num'} = $acc;
        
            # Parses the genbank file using the alignment obtained from parsing the BLAST results
            my $start_contig = $parse_blast{$scaffold}{'align'}->[0];
            my $end_contig = $parse_blast{$scaffold}{'align'}->[1];
            my $cnt = 0;
            foreach my $feat_o($seq_o->get_SeqFeatures()){
                my $start_f = $feat_o->start();
                my $end_f = $feat_o->end();
                my $prim = $feat_o->primary_tag();
                if (($end_f >= $start_contig) && ($start_f <= $end_contig) && ($prim eq 'CDS')) {
                    my $orf_id = $scaffold . '-' . ++$cnt;
                    my ($start, $end);
                    my $rf = $feat_o->strand();
                    my @tag_values = $feat_o->get_tagset_values(qw/product translation/);
                    my $annotation = $tag_values[0];
                    if (($start_f - $start_contig) < 0) {
                        $start = 1;
                        $annotation =~ s/^(.+)$/TRUNC:$1/;
                    } else {
                        $start = ($start_f - $start_contig);
                    }
                    if (($end_f - $start_contig) > ($end_contig - $start_contig)) {
                        $end = ($end_contig - $start_contig);
                        $annotation =~ s/^(.+)$/TRUNC:$1/;
                    } else {
                        $end = ($end_f - $start_contig);
                    }
                    
                    my $seq = $tag_values[1];
                    $contig_orf{$scaffold}->[1]{'genbank'}{$orf_id} = {
                                                                             'start'    => $start,
                                                                             'end'      => $end,
                                                                             'reading_frame' => $rf,
                                                                             'score'    => '',
                                                                             'annotation'   => $annotation,
                                                                             'sequence'     => $seq
                                                                            };
                }
            }
        }
    }
    
    store(\%parse_blast, "temp/storage/genbank.$$") or die "could not store";
    store (\%contig_orf, "temp/storage/contig.$$") or die "could not store";
    print $$;
}

sub getGenbank{
    my $arr_r = shift;
    my %acc_arr = %{$arr_r};
    my @arr;
    foreach my $scaf(keys(%acc_arr)){
        push(@arr, $acc_arr{$scaf});
    }
    getstore("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&rettype=gb&retmode=text&id=".join(",",@arr),"seqs.gb");
    my $in_o = Bio::SeqIO->new(-file    => '<seqs.gb',
                               -format  => 'genbank');
    while (my $seq_o = $in_o->next_seq()) {
        foreach my $scaf(keys(%acc_arr)){
            $acc_arr{$scaf} =~ /^(.+?)\.\d$/;
            my $accession = $1;
            if ($seq_o->accession_number() =~ /$accession/) {
                my $out_o = Bio::SeqIO->new(-file   => '>temp/genbank/' . $scaf . '.gbk',
                                    -format => 'genbank');
                $out_o->write_seq($seq_o);
            }
        } 
    }
}

sub parseBLAST{
    my $scaffold = shift;
    my ($acc, $start, $end, @start_orf, @end_orf);
    opendir(my $contig_fh, "temp/data/blast");
    my @contig_blasts = grep{/.+?\.blast/} readdir($contig_fh);
    foreach my $blast_file(@contig_blasts){
        if ($blast_file =~ /$scaffold/) {
            my $blast_o = Bio::SearchIO->new(-format => 'blast',
                                             -file => "temp/data/blast/$scaffold" . '.blast');
            if(my $result_o = $blast_o->next_result()){
                if(my $hit_o = $result_o->next_hit()){
                    $acc = $hit_o->accession();
                    my $count = 0;
                    while (my $hsp_o = $hit_o->next_hsp()) {
                        my @ends = $hsp_o->range('query');
                        push(@start_orf, $ends[0]);
                        push(@end_orf, $ends[1]);
                        if ($count == 0) {
                            my @first_hsp = $hsp_o->range('hit');
                            $start = $first_hsp[0] - $ends[0];
                            $end = $start + ($result_o->query_length());
                        }
                        $count++;
                    }
                }
            }
        }
    }
    closedir($contig_fh);
    my @start_end = ($start, $end);
    return($acc, \@start_end, \@start_orf, \@end_orf);
}

sub getCoordinate{
    my($_query, $_num) = @_;
    my ($start, $end);
    
    return($start, $end);
}