#!/usr/bin/perl
use warnings;
use strict;
use lib '/usr/share/perl5';
use lib '/usr/lib/cpan/custom/';
use lib '/usr/lib/cpan/custom/BioPerl';
use lib '/usr/lib/cpan/custom/Storable/blib/lib';
use Bio::Seq;
use Bio::SeqIO;
use Data::Dumper;
use Storable;
use Cwd;

my $cwd = $ARGV[0];
chdir($cwd);
s
open(my $data, "<", "data.lib") or die "Could not open data.lib file: $!\n";

require "data.lib";
my $contig_ref = data();
my %contig_orf = %{$contig_ref};
foreach my $scaf(keys(%contig_orf)){
    my $seq_o = Bio::Seq->new(-display_id => $scaf,
                              -seq => $contig_orf{$scaf}->[0]);
    my $outseq_o = Bio::SeqIO->new(-file => ">temp/data/$scaf.fa",
                                   -format => 'fasta');
    $outseq_o->write_seq($seq_o);
}

store (\%contig_orf, "temp/storage/contig.$$") or die "could not store";
print $$;
