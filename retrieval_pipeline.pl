#!/usr/bin/perl
use warnings;
use strict;

if (scalar(@ARGV == 3)) {
    my ($f_file, $r_file, $database) = @ARGV;
    #my $pid = `perl endtag.pl $f_file $r_file $database`;
    
    my $ping = `ping -c 1 orca.sharcnet.ca`;
    if ($ping) {
        print "Ping $ping\n";
    }else {
        print "Ping 1 FAILED\n";
    }
    
    #system("perl endtag_write.pl $pid")
} else {
    print help();
}

sub help{
    my $help = <<HELPFILE;
    *****************************************
    *         Contig Retrieval Tool         *
    *****************************************
    * This tool requires 3 fields:          *
    *       - Forward endtag .csv file      *
    *       - Reverse endtag .csv file      *
    *       - Database .fa file             *
    * This tool will match up the end tags  *
    * to the appropriate contig for both    *
    * F_ and R_ endtag.  It will determine  *
    * the match between the retrieved       *
    * contigs, as well as identify and      *
    * annotate every ORF found on the       *
    * retrieved contig.                     *
    *                                       *
    * Output will be a:                     *
    *       - pdf containing summary        *
    *       - csv file to return to db      *
    *       - image generated for each      *
    *       retrieved contig                *
    *****************************************
HELPFILE
    return $help;
}