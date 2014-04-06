#!/usr/bin/perl
use warnings;
use strict;
use lib '/usr/lib/cpan/custom/GD';
use lib '/usr/share/perl5';
use lib '/usr/lib/cpan/custom/BioGraphics/lib';
use lib '/usr/lib/cpan/custom/BioGraphics2/lib';
use lib '/usr/lib/cpan/custom/BioPerl-SABP/lib/';
use lib '/usr/lib/cpan/custom/BioPerl';
use lib '/usr/lib/cpan/custom/Storable/blib/lib/';
use Bio::Seq;
use Bio::Tools::Run::StandAloneBlastPlus;
use Spreadsheet::ParseExcel;
use Spreadsheet::WriteExcel;
use Bio::AlignIO;
use Bio::SearchIO;
use Bio::SeqIO;
use Data::Dumper;
use Bio::Graphics;
use Bio::SeqFeature::Generic;
use File::Path qw/make_path remove_tree/;
use Data::Dumper;
use Storable;
use Cwd;

my $bgcolor = "blue";
my $_strand;

my %contig_orf;
my %genbank;
my %_contig_retrieval;
my $_pad_right = 400;
if ((scalar(@ARGV)) == 3) {
    
    my ($parentid2, $cwd, $dir) = @ARGV;
    chdir("$cwd");

    my $_contig_orf = retrieve("temp/storage/contig.$parentid2") or die "Could not retrieve Contig orf $!\n";
    %contig_orf = %{$_contig_orf};
    outputAnnoCSV(\%contig_orf, $dir);




    foreach my $scaffold(sort(keys(%contig_orf))){

        my $contig_len = length($contig_orf{$scaffold}->[0]);
        my $width;
        ($contig_len > 6000) ? ($width = $contig_len / 7.5) : ($width = 800);
        my $contig_desc = $scaffold;
        my $feature;
        if ($contig_len > 1) {
 
                
#-----------------------------------------------------------------------------------------------
#                       Bio:Graphics - Makes the Image
#-----------------------------------------------------------------------------------------------
    #                       CONTIG Panel
    #-------------------------------------------------------------------------------------------
            my $panel_contig = Bio::Graphics::Panel->new(
                                                -length =>  $contig_len,   #length of segment sequence in bp
                                                -key_style => 'between',
                                                -width  =>  $width,    #width of image in pixels (600 default)
                                                -pad_left   =>  10, #Adds white space padding
                                                -pad_right  =>  $_pad_right,
                                            );
            my $contig_seq = Bio::SeqFeature::Generic->new(
                                                          -start    =>  1,
                                                          -end      =>  $contig_len,
                                                          -display_name =>  $contig_desc);
            
            #-------------SCALE TRACK--------------------
            $panel_contig->add_track($contig_seq,
                              -glyph    =>  'arrow',
                              -tick =>  2,  # sets both major and minor tick marks
                              -fgcolor  =>  'black',
                              -double   =>  1,  #double ended arrows
                              );
            
            #------------CONTIG TRACK--------------------
            $panel_contig->add_track($contig_seq,
                              -glyph    =>  'generic',
                              -bgcolor  =>  $bgcolor,
                              -label    =>  1,
                              -height   =>  20
                             );
            
            open(my $output_contig, ">", "$dir/img/$contig_desc" . "-CONTIG.png") or die ("could not create, $!\n");
            print $output_contig $panel_contig->png;
            close($output_contig);
    
        #-------------------------------------------------------------------------------------------
        #                       GENBANK Panel
        #-------------------------------------------------------------------------------------------

            my $panel_gen = Bio::Graphics::Panel->new(
                                                -length =>  $contig_len,   #length of segment sequence in bp
                                                -key_style => 'between',
                                                -width  =>  $width,    #width of image in pixels (600 default)
                                                -pad_left   =>  10, #Adds white space padding
                                                -pad_right  =>  $_pad_right,
                                            );

            my $genbank_track = $panel_gen->add_track($feature,
                            -glyph  =>  'transcript2',
                            -stranded => 1,
                            -label  =>  1,
                            -key    => 'Genbank',
                            -bgcolor    =>  'green',
                            -height =>  10,
                            -font   =>  'gdLargeFont',
                            -font2color =>  'black',  #color for description
                            -bump   =>  2,
                            -description    =>  sub{
                                my $feat = shift;
                                my $anno = $feat->annotation;
                                my $st = $feat->start;
                                return "$anno, Start=$st";
                            },
                        );

            foreach(keys(%{$contig_orf{$scaffold}->[1]{'genbank'}})){
                unless ($contig_orf{$scaffold}->[1]{'genbank'}{$_}{'start'}) {
                    delete $contig_orf{$scaffold}->[1]{'genbank'}{$_};
                }
            }
            foreach my $retrieve(sort{$contig_orf{$scaffold}->[1]{'genbank'}{$a}{'start'} <=> $contig_orf{$scaffold}->[1]{'genbank'}{$b}{'start'}}keys(%{$contig_orf{$scaffold}->[1]{'genbank'}})){
                my $_gen_anno = $contig_orf{$scaffold}->[1]{'genbank'}{$retrieve}{'annotation'};
                unless($contig_orf{$scaffold}->[1]{'genbank'}{$retrieve}{'annotation'}){
                    $_gen_anno = '_';
                }
                if ($contig_orf{$scaffold}->[1]{'genbank'}{$retrieve}{'reading_frame'}) {
                    ($contig_orf{$scaffold}->[1]{'genbank'}{$retrieve}{'reading_frame'} > 0 ) ? ($_strand = 1) : ($_strand = -1);
                } else {
                    $_strand = 0;
                }
                
                $feature = Bio::SeqFeature::Generic->new(
                                                #-display_name   =>  $name[$i],
                                                -strand => $_strand,
                                                -score  =>  $contig_orf{$scaffold}->[1]{'genbank'}{$retrieve}{'score'},
                                                -annotation =>  $_gen_anno,
                                                -start  =>  $contig_orf{$scaffold}->[1]{'genbank'}{$retrieve}{'start'},     # Start of range
                                                -end    =>  $contig_orf{$scaffold}->[1]{'genbank'}{$retrieve}{'end'},        # End of range
                                                );
                $genbank_track->add_feature($feature);
            }
            
            open(my $output_gen, ">", "$dir/img/$contig_desc" . "-GENBANK.png") or die ("could not create, $!\n");
            print $output_gen $panel_gen->png;
            close($output_gen);
    
    #-------------------------------------------------------------------------------------------
    #                       GLIMMER Panel
    #-------------------------------------------------------------------------------------------
            my $panel_glim = Bio::Graphics::Panel->new(
                                                -length =>  $contig_len,   #length of segment sequence in bp
                                                -key_style => 'between',
                                                -width  =>  $width,    #width of image in pixels (600 default)
                                                -pad_left   =>  10, #Adds white space padding
                                                -pad_right  =>  $_pad_right,
                                            );
            
            #print "Glimmer RF: $contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'reading_frame'}\n"; 
            #($contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'reading_frame'} > 0 ) ? ($_strand = 1) : ($_strand = -1);
            my $glimmer_track = $panel_glim->add_track(
                $feature,
                -glyph  =>  'transcript2',
                -stranded => 1,
                -label  =>  1,
                -key    => "Predicted ORFs",
                -bgcolor    =>  'red',
                -height =>  10,
                -font   =>  'gdLargeFont',
                -font2color =>  'black',  #color for description
                -bump   =>  2,
                -description    =>  sub{
                    my $feat = shift;
                    my $anno = $feat->annotation;
                    my $score = $feat->score;
                    my $st = $feat->start;
                    return "$anno, Score=$score || Start=$st";
                },
            );
            
            if ($contig_orf{$scaffold}->[1]{'glimmer'}) {
                foreach my $retrieve(sort{$contig_orf{$scaffold}->[1]{'glimmer'}{$a}{'start'} <=> $contig_orf{$scaffold}->[1]{'glimmer'}{$b}{'start'}}keys(%{$contig_orf{$scaffold}->[1]{'glimmer'}})){
                    my $_glim_anno = $contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'annotation'};
                    unless($contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'annotation'}){
                        $_glim_anno = '_';
                    }
                    
                    if ($contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'reading_frame'}) {
                        ($contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'reading_frame'} > 0 ) ? ($_strand = 1) : ($_strand = -1);
                    } else {
                        $_strand = 0;
                    }
                    
                    $feature = Bio::SeqFeature::Generic->new(
                                                    #-display_name   =>  $name[$i],
                                                    -strand => $_strand,
                                                    -score  =>  $contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'score'},
                                                    -annotation =>  $_glim_anno,
                                                    -start  =>  $contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'start'},     # Start of range
                                                    -end    =>  $contig_orf{$scaffold}->[1]{'glimmer'}{$retrieve}{'end'},        # End of range
                                                    );
                    $glimmer_track->add_feature($feature);
                }
            }
            
            
            open(my $output_glim, ">", "$dir/img/$contig_desc" . "-GLIM.png") or die ("could not create, $!\n");
            print $output_glim $panel_glim->png;
            close($output_glim);
    #-------------------------------------------------------------------------------------------
    #                       ALIGNMENT Panel
    #-------------------------------------------------------------------------------------------
            my $blastfile_o = Bio::SearchIO->new(-file => "temp/data/blast/$scaffold.blast",
                                                 -format => 'blast');
            if(my $result_o = $blastfile_o->next_result()){
                if (my $hit_o = $result_o->next_hit()) {
                    
                    my $panel_align = Bio::Graphics::Panel->new(
                                                        -length =>  $contig_len,   #length of segment sequence in bp
                                                        -key_style => 'between',
                                                        -width  =>  $width,    #width of image in pixels (600 default)
                                                        -pad_left   =>  10, #Adds white space padding
                                                        -pad_right  =>  $_pad_right,
                                                    );
                    
                    my $align_track = $panel_align->add_track(
                                    -glyph  =>  'graded_segments',
                                    -label  =>  1,
                                    -key    => "Genbank Top Hit Aligned",
                                    -connector => 'dashed',
                                    -bgcolor    =>  $bgcolor,
                                    -height =>  10,
                                    -fgcolor     => 'black',
                                    -font   =>  'gdLargeFont',
                                    -font2color =>  'black',  #color for description
                                    -description    =>  sub{
                                        my $feat = shift;
                                        return unless $feat->has_tag('description');
                                        my ($description) = $feat->each_tag_value('description');
                                        my $score = $feat->score;
                                        "$description, Score=$score";
                                    },
                                );
                    
                    $feature = Bio::SeqFeature::Generic->new(-score    => $hit_o->raw_score(),
                                                                  -display_name => $hit_o->name(),
                                                                  -tag  => {description => $hit_o->description()});
                    while (my $hsp_o = $hit_o->next_hsp()) {
                        $feature->add_sub_SeqFeature($hsp_o, 'EXPAND');
                    }
                    $align_track->add_feature($feature);
                    
                    open(my $output_align, ">", "$dir/img/$contig_desc" . "-ALIGN.png") or die ("could not create, $!\n");
                    print $output_align $panel_align->png;
                    close($output_align);
                }
            }
            
            

    #-------------------------------------------------------------------------------------------
    #                       MANUAL Panel
    #-------------------------------------------------------------------------------------------
            my $panel_manual = Bio::Graphics::Panel->new(
                                                -length =>  $contig_len,   #length of segment sequence in bp
                                                -key_style => 'between',
                                                -width  =>  $width,    #width of image in pixels (600 default)
                                                -pad_left   =>  10, #Adds white space padding
                                                -pad_right  =>  $_pad_right,
                                            );
            
            #($contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'reading_frame'} > 0 ) ? ($_strand = 1) : ($_strand = -1);
            my $manual_track = $panel_manual->add_track(
                            -glyph  =>  'transcript2',
                            -stranded => 1,
                            -label  =>  1,
                            -key    => 'Manual',
                            -bgcolor    =>  'yellow',
                            -height =>  10,
                            -font   =>  'gdLargeFont',
                            -font2color =>  'black',  #color for description
                            -bump   =>  2,
                            -description    =>  sub{
                                my $feat = shift;
                                my $anno = $feat->annotation;
                                my $st = $feat->start;
                                return "$anno, Start=$st";
                            },
                        );
            
            foreach my $retrieve(sort{$contig_orf{$scaffold}->[1]{'manual'}{$a}{'start'} <=> $contig_orf{$scaffold}->[1]{'manual'}{$b}{'start'}}keys(%{$contig_orf{$scaffold}->[1]{'manual'}})){
                my $_man_anno = $contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'annotation'};
                unless($contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'annotation'}){
                    $_man_anno = '_';
                }
                if ($contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'reading_frame'}) {
                    ($contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'reading_frame'} > 0 ) ? ($_strand = 1) : ($_strand = -1);
                } else {
                    $_strand = 0;
                }
                
                $feature = Bio::SeqFeature::Generic->new(
                                                #-display_name   =>  $name[$i],
                                                -strand => $_strand,
                                                -score  =>  $contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'score'},
                                                -annotation =>  $_man_anno,
                                                -start  =>  $contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'start'},     # Start of range
                                                -end    =>  $contig_orf{$scaffold}->[1]{'manual'}{$retrieve}{'end'},        # End of range
                                                );
                $manual_track->add_feature($feature);
            }
            
            open(my $output_manual, ">", "$dir/img/$contig_desc" . "-MANUAL.png") or die ("could not create, $!\n");
            print $output_manual $panel_manual->png;
            close($output_manual);
        }
    }
}

sub outputAnnoCSV{
    my ($contig_r, $dir) = @_;
    my %contig_orf = %{$contig_r};
    open(my $outcsv, ">>", "$dir/out/annotations.csv") or die "Could not create the annotation csv: $!\n";
    foreach my $scaf(keys(%contig_orf)){
        my $seq = $contig_orf{$scaf}->[0];
        $seq =~ s/(\n)|(\r)//g;
        my $acc = $contig_orf{$scaf}->[2];
        print "HERE: $scaf and $acc\n";
        foreach my $orf(sort(keys(%{$contig_orf{$scaf}->[1]{'glimmer'}}))){
            print $outcsv "$scaf, $orf, $seq, $acc, $contig_orf{$scaf}->[1]{'glimmer'}{$orf}{'sequence'}, $contig_orf{$scaf}->[1]{'glimmer'}{$orf}{'annotation'}, $contig_orf{$scaf}->[1]{'glimmer'}{$orf}{'start'}, $contig_orf{$scaf}->[1]{'glimmer'}{$orf}{'end'}, $contig_orf{$scaf}->[1]{'glimmer'}{$orf}{'reading_frame'}, $contig_orf{$scaf}->[1]{'glimmer'}{$orf}{'score'}\n";
        }
    }
}

 
__END__   
   