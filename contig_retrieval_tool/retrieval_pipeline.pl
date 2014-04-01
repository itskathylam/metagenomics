#!/usr/bin/perl
use warnings;
use strict;

if (scalar(@ARGV == 3)) {
    my ($f_file, $r_file, $database) = @ARGV;
    my $pid = `perl endtag_setup.pl $f_file $r_file $database`;
    $pid = `perl endtag_match.pl $pid`;
=pod
    my $ping = `ping -c 1 orca.sharcnet.ca`;
    if ($ping) {
        print "Ping $ping\n";
    }else {
        print "Ping 1 FAILED\n";
    }
    
=cut
    $pid = `perl endtag_orf.pl $pid`;
    $pid = `perl endtag_graphics.pl $pid`;
    print $pid, "\n";
    #$pid = `perl endtag_annot.pl $pid`;
    
    system('rm -rf testdb*');
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

__END__
#!/bin/bash
sqsub -r 15m -n 16 -q mpi --mpp=1G -o ofile%J mpirun -np 16 --machinefile $PBS_NODEFILE mpiblast -d drosoph.nt -i drosoph.fa -p blastn -o drosoph.out --use-parallel-write --use-virtual-frags
/opt/sharcnet/openmpi/1.6.2/intel/bin/mpirun -np 16 --machinefile $PBS_NODEFILE mpiblast -d drosoph.nt -i drosoph2.fa -p blastn -o drosoph2.out --use-parallel-write --use-virtual-frags
/opt/sharcnet/openmpi/1.6.2/intel/bin/mpirun -np 16 --machinefile $PBS_NODEFILE mpiblast -d drosoph.nt -i drosoph3.fa -p blastn -o drosoph3.out --use-parallel-write --use-virtual-frags
sqsub -r 15m -n 16 -q mpi --mpp=1G -o ofile%J ./run.sh
sqjobs | egrep -o '[0-9]+?\s*?mpi\s*?R' | egrep -o '[0-9]+'
sqjobs | egrep -o '3670361+?\s*?mpi\s*?.' | egrep -o '[A-Z]'
