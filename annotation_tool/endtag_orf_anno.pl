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
    
    opendir(my $predict_blast_fh, "temp/predicts/blast");
    my @predict_blast = grep{/.+\.blast$/} readdir($predict_blast_fh);
    foreach my $scaffold(keys(%contig_orf)){
        foreach my $blast_file(@predict_blast){
            if ($blast_file =~ /$scaffold/) {
                my $blast_o = Bio::SearchIO->new(-file => "temp/predicts/blast/$blast_file",
                                                 -format => 'blast');
                my $orf_cnt = 1;
                while (my $result_o = $blast_o->next_result()) {
                    #print "-----------------------------------------\n";
                    #print "NEXT RESULT\n";
                    my $query_name = $result_o->query_name();
                    if ($query_name =~ /$scaffold\_(\d+?)_(\d+?)_/) {
                        my ($s, $e) = ($1, $2);
                        foreach my $id (sort keys($contig_orf{$scaffold}->[1]{'glimmer'})){
                            #print "$id Start: " . $s . " " . $contig_orf{$scaffold}->[1]{'glimmer'}{$id}{'start'}, "\n";
                            #print "$id End: " . $e . " " . $contig_orf{$scaffold}->[1]{'glimmer'}{$id}{'end'}, "\n";
                            if ($s == $contig_orf{$scaffold}->[1]{'glimmer'}{$id}{'start'} && $e == $contig_orf{$scaffold}->[1]{'glimmer'}{$id}{'end'}){
                                if(my $hit_o = $result_o->next_hit()){
                                    #print $hit_o->description, "\n";
                                    #print "Start: " . $s . " " . $contig_orf{$scaffold}->[1]{'glimmer'}{$id}{'start'}, "\n";
                                    #print "End: " . $e . " " . $contig_orf{$scaffold}->[1]{'glimmer'}{$id}{'end'}, "\n";
                                    my $anno = $hit_o->description();
                                    if ($anno =~ /(^.+?\[.+?\])/) {
                                        $anno = $1;
                                    }
                                    
                                    $contig_orf{$scaffold}->[1]{'glimmer'}{$id}{'annotation'} = $anno;
                                }
                            }
                        }
                    }
                }
            }
        }    
    }
    store (\%contig_orf, "temp/storage/contig.$$") or die "could not store";
    print $$;
}
__END__
