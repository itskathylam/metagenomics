#!/usr/bin/perl
use warnings;
use strict;
use Cwd qw/abs_path chdir/;
my $cwd;
if (abs_path('annotation_tool/annotation_pipeline.pl')) {
    $cwd = abs_path('annotation_tool/annotation_pipeline.pl');
} elsif (abs_path('annotation_pipeline.pl')){
    $cwd = abs_path('annotation_pipeline.pl');
}
$cwd =~ s/\/annotation_pipeline.pl//;
chdir("$cwd");

my $server = 'saw';
my $filename = 'mg_temp';
if (scalar(@ARGV == 1)) {
    if (setup() == 1) {
        # $status should be either: -update or -annotate
        my $status = $ARGV[0];
        open(my $log, ">>", "log.txt");
        
        # If the annotations are being created for the first time.
        # This will run a pipesline that will annotate each scaffold based on known genbank
        # annotations, and generate their own orf predictions based on FragGeneScan (Can
        # be changed to support Glimmer, or MetaGeneMark)
        
        if (($status eq '-annotate') && (-s 'data.lib')) {
            my $dir = "tool";
            print $log "********************************\nExecution of Contig Annotation Pipeline\n********************************\n";
            print $log "Retrieving contig information...";
            my $pid = `perl endtag_retrieve.pl $cwd`;
            
            # Makes ORF predictions on the contig based on FragGeneScan
            print $log "Predicting ORFs on Contigs using FragGeneScan v.1.16...\n";
            my $ret = FGS();
            
            # Script to parse out all relevant information except for annotations from the predict
            # files created by FragGeneScan. 
            print $log "Building predicted genes...\n";
            $pid = `perl endtag_orf.pl $pid $cwd`;
            
            #Connecting to Sharcnet
            my $ping = `ping -c 1 $server.sharcnet.ca`;
            if ($ping) {
                print $log "Pinging $server.sharcnet.ca...\n";
                print $log "Ping $ping\n";
                system("echo \"$cwd\" > .message");
                `tar -cvf $filename.tar temp/ tmp/ .message`;
                
                # Transfer of temp/ folder to sharcnet: /scratch/kathylam/metagenomics
                print $log "Transfering contig information to Sharcnet...\n";
                `scp $filename.tar kathylam\@$server.sharcnet.ca:/scratch/kathylam/metagenomics/`;
                
                # Running of the sharcnet pipeline to obtain the annotations by blasting each
                # contig and predicted ORF
                print $log "Transfer Complete.\n Executing sharcnet BLAST pipeline...\n";
                my $return = `ssh kathylam\@$server.sharcnet.ca perl /scratch/kathylam/metagenomics/sharc_mg_pipe.pl`;
                
                #my $return = listenSN();
                print $log "Sharcnet pipeline status: $return \n";
                
                if ($return) {
                    chdir("$cwd");
                    print $log "Sharcnet Stage Complete.\n";
                    if (-s 'sharcnet_anno.tar') {
                        print $log "Received Blast Files: Extracting sharcnet_anno.tar...\n";
                        my $val = `tar -xmvf sharcnet_anno.tar`;
                        
                        # From the BLAST files retrieved from sharcnet, it will create the annotations
                        # for each predicted ORF
                        print $log "Annotating predicted ORFs...\n";
                        $pid = `perl endtag_orf_anno.pl $pid $cwd`;
                        
                        # From the BLAST files retrieved from sharcnet, it will extract the
                        # accession number and retrieve their respective genbank document.  The
                        # genbank documnet will be parsed for CDS information
                        print $log "Retrieving and annotating genbank information...\n";
                        $pid = `perl endtag_genbank.pl $pid $cwd`;
                        
                        #Generates the graphics based on all the cumulative data.
                        print $log "Generating graphics...\n";
                        $pid = `perl endtag_graphics.pl $pid $cwd $dir`;
                        print $log "Images have been generated!\n Annotation complete\n";
                    }
                }
            }else {
                print $log "Sharcnet Status: Unreachable\n";
            }
        # If the annotations already exist and manual annotations are being added
        # The arguement -update will append exisiting manual annotations to the graphics
        # generated.  However, it will regenerate the genbank annotations in order to make
        # them more recent.
        } elsif(($status eq '-update') && (-s 'data.lib')){
            my $dir = 'tmp';
            print $log "********************************\nUpdating Contig Annotations\n********************************\n";
            my $pid = `perl endtag_retrieve.pl $cwd`;
            print $log "ParentID: $pid\n";
            
            # Will use accession number to retrieve their respective genbank document.  The
            # genbank documnet will be parsed for CDS information
            print $log "Retrieving Genbank information and updating Blast alignments...\n";
            $pid = `perl endtag_genbank_update.pl $pid $cwd`;
            
            #Generates the graphics based on all the cumulative data.
            print $log "Generating graphics...\n";
            $pid = `perl endtag_graphics.pl $pid $cwd $dir`;
            print $log "Images have been generated!\n Annotation update complete\n";          
        }
        #cleanUp();   
    }
} else {
    print help();
}


sub cleanUp{
    system('rm seqs.gb');
    system('rm data.lib');
    system('rm -rf temp/');
    system('rm -rf testdb*'); 
}

sub setup{
    my $ret = 0;
    (system("mkdir temp")) unless (-d "temp");
    (system("mkdir -p tool/img")) unless (-d "tool/img");
    (system("mkdir -p tool/out")) unless (-d "tool/out");
    (system("mkdir temp/tmp")) unless (-d "temp/tmp");
    (system("mkdir -p tmp/out")) unless (-d "tmp/out");
    (system("mkdir -p temp/data/blast")) unless (-d "temp/data");
    (system("mkdir tmp/img")) unless (-d "tmp/img");
    (system("mkdir temp/orf_seq")) unless (-d "temp/orf_seq");
    (system("mkdir -p temp/predicts/blast")) unless (-d "temp/predicts");
    (system("mkdir temp/storage")) unless (-d "temp/storage");
    (system("mkdir temp/genbank")) unless (-d "temp/genbank");
    if ((-d "temp/tmp") && (-d "temp/data") && (-d "tool/img") && (-d "tool/out") && (-d "tmp/img") && (-d "tmp/out") && (-d "temp/genbank") && (-d "temp/orf_seq") && (-d "temp/predicts") && (-d "temp/storage")){
        $ret = 1;
    }
    return $ret;
}

sub FGS{
    opendir(my $contig_dir, "temp/data");
    my @files = grep{/.+?\.fa/} readdir($contig_dir);
    foreach my $filename(@files){
        $filename =~ /(.+?)\.fa/;
        my $filename_trunc = $1;
        `perl /home/project/metagenomics/bin/FragGeneScan1.16/run_FragGeneScan.pl -genome=./temp/data/$filename -out=./temp/predicts/$filename_trunc  -complete=1  -train=complete`;
    }
    closedir($contig_dir);
    opendir(my $predict_dir, "temp/predicts");
    my @predict_files = readdir($predict_dir);
    my $ret = 0;
    if (scalar(@predict_files) == (scalar(@files) * 3 + 2)) {
        $ret = 1;
    }
    return($ret);
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
