#!/usr/bin/perl
use warnings;
use strict;
use Cwd qw/abs_path chdir/;
my $cwd;
if (abs_path('contig_retrieval_tool/retrieval_pipeline.pl')) {
    $cwd = abs_path('contig_retrieval_tool/retrieval_pipeline.pl');
} elsif (abs_path('retrieval_pipeline.pl')){
    $cwd = abs_path('retrieval_pipeline.pl');
}
$cwd =~ s/\/retrieval_pipeline.pl//;
chdir("$cwd");

my $server = 'saw';
my $filename = 'mg_temp';
if (scalar(@ARGV) == 3) {
    open(my $log, ">>", "log.txt");
    if (setup() == 1) {
        my ($f_file, $r_file, $database) = @ARGV;
        $f_file = $cwd . '/' . $f_file;
        $r_file = $cwd . '/' . $r_file;
        $database = $cwd . '/' . $database;
        
        print $log "********************************\nExecution of Contig Retrieval Pipeline\n********************************\n";
        print $log "Executing Endtag Setup\n";
        my $pid = `perl endtag_setup.pl $f_file $r_file $database $cwd`;
        
        print "$pid and $cwd\n";
        #10961 and /home/rene/metagenomics/contig_retrieval_tool
        print $log "Matching the contigs to the cosmids\n";
        $pid = `perl endtag_match.pl $pid $cwd`;
        print $log "Contigs Retrieval Complete\n";     

        system('rm -rf testdb*');
        #cleanUp();
    }

} else {
    print help();
}


sub cleanUp{
    system('rm data.lib');
    system('rm contigs.fa');
    system('rm primers_*');
    system('rm -rf temp/');
    #system('rm -rf tmp/');
    system('rm .message');
    #system('rm .pid');
}

sub setup{
    my $ret = 0;
    (system("mkdir temp")) unless (-d "temp");    
    (system("mkdir -p temp/tmp")) unless (-d "temp/tmp");
    (system("mkdir -p tmp/out")) unless (-d "tmp/out");
    (system("mkdir -p temp/data/blast")) unless (-d "temp/data");
    (system("mkdir -p tmp/img")) unless (-d "tmp/img");
    (system("mkdir temp/orf_seq")) unless (-d "temp/orf_seq");
    (system("mkdir -p temp/predicts/blast")) unless (-d "temp/predicts");
    (system("mkdir temp/storage")) unless (-d "temp/storage");
    (system("mkdir temp/genbank")) unless (-d "temp/genbank");
    if ((-d "temp/tmp") && (-d "temp/data") && (-d "tmp/img") && (-d "tmp/out") && (-d "temp/genbank") && (-d "temp/orf_seq") && (-d "temp/predicts") && (-d "temp/storage")){
        $ret = 1;
    }
    return $ret;
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

