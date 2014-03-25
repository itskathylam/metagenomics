#!/usr/bin/perl
use warnings;
use strict;
BEGIN {
    $ENV{BLASTPLUSDIR} = '/home/rene/endtags/end/install/ncbi-blast-2.2.29+-src/c++/ReleaseMT/bin';
    $ENV{PATH} .= ':/usr/bin/emboss/emboss';
}
use lib '/usr/lib/cpan/custom/GD';
use lib '/usr/share/perl5';
#use lib '/usr/bin/emboss/emboss';
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


my $bgcolor = "blue";



if (scalar(@ARGV) == 1) {
    my $parentid = $ARGV[0];
    my $_contig_retrieval = retrieve("storage/write.$parentid") or die "Could not retrieve $!\n";
    my %_contig_retrieval = %{$_contig_retrieval};
    
    foreach my $query(sort(keys(%_contig_retrieval))){
        foreach my $iden(sort(keys(%{$_contig_retrieval{$query}}))){
            my (@cons_start, @glim_start, @gen_start, @man_start) = ();
            my (@cons_end, @glim_end, @gen_end, @man_end) = ();
            my (@cons_anno, @glim_anno, @gen_anno, @man_anno) = ();
            if ($_contig_retrieval{$query}{$iden}->[15] == 1 ||$_contig_retrieval{$query}{$iden}->[15] == 2 ||$_contig_retrieval{$query}{$iden}->[15] == 3) {
                my @anno_array = qw/consensus glimmer genbank manual/;
                foreach my $name(@anno_array){
                    foreach my $retrieve(sort(keys($_contig_retrieval{$query}{$iden}->[14]{$name}))){
                        if ($name eq 'consensus') {
                            push(@cons_start, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'start'});
                            push(@cons_end, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'end'});
                            push(@cons_anno, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'annotation'});
                        } elsif ($name eq 'glimmer'){
                            push(@glim_start, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'start'});
                            push(@glim_end, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'end'});
                            push(@glim_anno, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'annotation'});
                        } elsif ($name eq 'genbank'){
                            push(@gen_start, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'start'});
                            push(@gen_end, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'end'});
                            push(@gen_anno, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'annotation'});
                        } elsif ($name eq 'manual'){
                            push(@man_start, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'start'});
                            push(@man_end, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'end'});
                            push(@man_anno, $_contig_retrieval{$query}{$iden}->[14]{$name}{$retrieve}{'annotation'});
                        } 
                    }
                }
                my $contig_len = length($_contig_retrieval{$query}{$iden}->[13]);
                my $width;
                ($contig_len > 6000) ? ($width = $contig_len / 7.5) : ($width = 800);
                $_contig_retrieval{$query}{$iden}->[1] =~ /lcl\|(.+)/;
                my $contig_desc = $1 . '--' . $query . '-' . $iden;
                
                #test
                push(@cons_start, 900);
                push(@cons_end, 1244);
                push(@glim_start, 2000);
                push(@glim_end, 2244);
                push(@gen_start, 1500);
                push(@gen_end, 2000);
                push(@man_start, 1500);
                push(@man_end,5000);
                #/test
                
                if (scalar(@glim_start) > 0) {
 
                
#-----------------------------------------------------------------------------------------------
#                       Bio:Graphics - Makes the Image
#-----------------------------------------------------------------------------------------------
                    my $panel = Bio::Graphics::Panel->new(
                                                        -length =>  $contig_len,   #length of segment sequence in bp
                                                        -key_style => 'between',
                                                        -width  =>  $width,    #width of image in pixels (600 default)
                                                        -pad_left   =>  10, #Adds white space padding
                                                        -pad_right  =>  10,
                                                    );
                    my $contig_seq = Bio::SeqFeature::Generic->new(
                                                                  -start    =>  1,
                                                                  -end      =>  $contig_len,
                                                                  -display_name =>  $contig_desc);
                    
                    #-------------SCALE TRACK--------------------
                    $panel->add_track($contig_seq,
                                      -glyph    =>  'arrow',
                                      -tick =>  2,  # sets both major and minor tick marks
                                      -fgcolor  =>  'black',
                                      -double   =>  1,  #double ended arrows
                                      );
                    
                    #------------CONTIG TRACK--------------------
                    $panel->add_track($contig_seq,
                                      -glyph    =>  'generic',
                                      -bgcolor  =>  $bgcolor,
                                      -label    =>  1,
                                      -height   =>  20
                                     );
                    
                    #-----------ORF TRACK------------------------
                    
                    my $consensus_track = $panel->add_track(
                                    -glyph  =>  'graded_segments',
                                    -label  =>  1,
                                    -key    => 'Consensus',
                                    -connector => 'dashed',
                                    #-tkcolor    =>  'turquoise',
                                    -bgcolor    =>  'turquoise',
                                    -fgcolor     => 'black',
                                    -height =>  10,
                                    -font   =>  'gdLargeFont',
                                    #-min_score  =>  0,
                                    #-max_score  =>  1000,
                                    -font2color =>  'red',  #color for description
                                    -sort_order =>  'high_score',
                                    -bump   =>  1,
                                    -description    =>  sub{
                                        my $feature = shift;
                                        my $anno = $feature->annotation;
                                        return "$anno";
                                    },
                                );  
                    my $glimmer_track = $panel->add_track(
                                    -glyph  =>  'graded_segments',
                                    -label  =>  1,
                                    -key    => "Glimmer",
                                    -connector => 'dashed',
                                    #-tkcolor    =>  'turquoise',
                                    -bgcolor    =>  'red',
                                    -fgcolor     => 'black',
                                    -height =>  10,
                                    -font   =>  'gdLargeFont',
                                    #-min_score  =>  0,
                                    #-max_score  =>  1000,
                                    -font2color =>  'red',  #color for description
                                    -sort_order =>  'high_score',
                                    -bump   =>  1,
                                    -description    =>  sub{
                                        my $feature = shift;
                                        my $anno = $feature->annotation;
                                        return "$anno";
                                    },
                                );
                    my $genbank_track = $panel->add_track(
                                    -glyph  =>  'graded_segments',
                                    -label  =>  1,
                                    -key    => 'Genbank',
                                    -connector => 'dashed',
                                    #-tkcolor    =>  'turquoise',
                                    -bgcolor    =>  'green',
                                    -height =>  10,
                                    -fgcolor     => 'black',
                                    -font   =>  'gdLargeFont',
                                    #-min_score  =>  0,
                                    #-max_score  =>  1000,
                                    -font2color =>  'red',  #color for description
                                    -sort_order =>  'high_score',
                                    -bump   =>  1,
                                    -description    =>  sub{
                                        my $feature = shift;
                                        my $anno = $feature->annotation;
                                        return "$anno";
                                    },
                                );
                    my $manual_track = $panel->add_track(
                                    -glyph  =>  'graded_segments',
                                    -label  =>  1,
                                    -key    => 'Manual',
                                    -connector => 'dashed',
                                    #-tkcolor    =>  'turquoise',
                                    -bgcolor    =>  'yellow',
                                    -fgcolor     => 'black',
                                    -height =>  10,
                                    -font   =>  'gdLargeFont',
                                    #-min_score  =>  0,
                                    #-max_score  =>  1000,
                                    -font2color =>  'red',  #color for description
                                    -sort_order =>  'high_score',
                                    -bump   =>  1,
                                    -description    =>  sub{
                                        my $feature = shift;
                                        my $anno = $feature->annotation;
                                        return "$anno";
                                    },
                                );
                
                
                
                    foreach my $i(0..(scalar(@cons_start)-1)){
                        my $feature = Bio::SeqFeature::Generic->new(
                                                        #-display_name   =>  $name[$i],
                                                        #-annotation  =>  $annotation[$i],
                                                        -annotation =>  "x",
                                                        -start  =>  $cons_start[$i],     # Start of range
                                                        -end    =>  $cons_end[$i],        # End of range
                                                        );
                        $consensus_track->add_feature($feature);
                    }
                    foreach my $i(0..(scalar(@glim_start)-1)){
                        my $feature = Bio::SeqFeature::Generic->new(
                                                        #-display_name   =>  $name[$i],
                                                        #-annotation  =>  $annotation[$i],
                                                        -annotation =>  "x",
                                                        -start  =>  $glim_start[$i],     # Start of range
                                                        -end    =>  $glim_end[$i],        # End of range
                                                        );
                        $glimmer_track->add_feature($feature);
                    }
                    foreach my $i(0..(scalar(@gen_start)-1)){
                        my $feature = Bio::SeqFeature::Generic->new(
                                                        #-display_name   =>  $name[$i],
                                                        #-annotation  =>  $annotation[$i],
                                                        -annotation =>  "x",
                                                        -start  =>  $gen_start[$i],     # Start of range
                                                        -end    =>  $gen_end[$i],        # End of range
                                                        );
                        $genbank_track->add_feature($feature);
                    }
                    foreach my $i(0..(scalar(@man_start)-1)){
                        my $feature = Bio::SeqFeature::Generic->new(
                                                        #-display_name   =>  $name[$i],
                                                        #-annotation  =>  $annotation[$i],
                                                        -annotation =>  "x",
                                                        -start  =>  $man_start[$i],     # Start of range
                                                        -end    =>  $man_end[$i],        # End of range
                                                        );
                        $manual_track->add_feature($feature);
                    }
                    
                    my $output_name = $contig_desc . ".png";
                    open(my $output, ">", "img/$output_name") or die ("could not create, $!\n");
                    print $output $panel->png;
#-----------------------------------------------------------------------------------------------
#                       \Bio:Graphics
#-----------------------------------------------------------------------------------------------
                }
                
            }
        }
    }
}

 
__END__   
    my $panel = Bio::Graphics::Panel->new(
                                        -length =>  $contig_len,   #length of segment sequence in bp
                                        -width  =>  $width,    #width of image in pixels (600 default)
                                        -pad_left   =>  10, #Adds white space padding
                                        -pad_right  =>  10,
                                    );
    my $contig_seq = Bio::SeqFeature::Generic->new(
                                                  -start    =>  1,
                                                  -end      =>  $contig_len,
                                                  -display_name =>  $contig_desc);
    
    #-------------SCALE TRACK--------------------
    $panel->add_track($contig_seq,
                      -glyph    =>  'arrow',
                      -tick =>  2,  # sets both major and minor tick marks
                      -fgcolor  =>  'black',
                      -double   =>  1,  #double ended arrows
                      );
    
    #------------CONTIG TRACK--------------------
    $panel->add_track($contig_seq,
                      -glyph    =>  'generic',
                      -bgcolor  =>  $bgcolor,
                      -label    =>  1,
                      -height   =>  20
                     );
    
    #-----------ORF TRACK------------------------
    
    my $consensus_track = $panel->add_track(
                    -glyph  =>  'graded_segments',
                    -label  =>  1,
                    -connector => 'dashed',
                    #-tkcolor    =>  'turquoise',
                    -bgcolor    =>  'turquoise',
                    -height =>  10,
                    -font   =>  'gdLargeFont',
                    #-min_score  =>  0,
                    #-max_score  =>  1000,
                    -font2color =>  'red',  #color for description
                    -sort_order =>  'high_score',
                    -bump   =>  1,
                    -description    =>  sub{
                        my $feature = shift;
                        my $anno = $feature->annotation;
                        return "$anno";
                    },
                );  
    my $glimmer_track = $panel->add_track(
                    -glyph  =>  'graded_segments',
                    -label  =>  1,
                    -connector => 'dashed',
                    #-tkcolor    =>  'turquoise',
                    -bgcolor    =>  'turquoise',
                    -height =>  10,
                    -font   =>  'gdLargeFont',
                    #-min_score  =>  0,
                    #-max_score  =>  1000,
                    -font2color =>  'red',  #color for description
                    -sort_order =>  'high_score',
                    -bump   =>  1,
                    -description    =>  sub{
                        my $feature = shift;
                        my $anno = $feature->annotation;
                        return "$anno";
                    },
                );
    my $genbank_track = $panel->add_track(
                    -glyph  =>  'graded_segments',
                    -label  =>  1,
                    -connector => 'dashed',
                    #-tkcolor    =>  'turquoise',
                    -bgcolor    =>  'turquoise',
                    -height =>  10,
                    -font   =>  'gdLargeFont',
                    #-min_score  =>  0,
                    #-max_score  =>  1000,
                    -font2color =>  'red',  #color for description
                    -sort_order =>  'high_score',
                    -bump   =>  1,
                    -description    =>  sub{
                        my $feature = shift;
                        my $anno = $feature->annotation;
                        return "$anno";
                    },
                );
    my $manual_track = $panel->add_track(
                    -glyph  =>  'graded_segments',
                    -label  =>  1,
                    -connector => 'dashed',
                    #-tkcolor    =>  'turquoise',
                    -bgcolor    =>  'turquoise',
                    -height =>  10,
                    -font   =>  'gdLargeFont',
                    #-min_score  =>  0,
                    #-max_score  =>  1000,
                    -font2color =>  'red',  #color for description
                    -sort_order =>  'high_score',
                    -bump   =>  1,
                    -description    =>  sub{
                        my $feature = shift;
                        my $anno = $feature->annotation;
                        return "$anno";
                    },
                );



    foreach my $i(0..(scalar(@start)-1)){
        my $feature = Bio::SeqFeature::Generic->new(
                                        #-display_name   =>  $name[$i],
                                        #-annotation  =>  $annotation[$i],
                                        -annotation =>  "x",
                                        -start  =>  $start[$i],     # Start of range
                                        -end    =>  $end[$i],        # End of range
                                        );
        $consensus_track->add_feature($feature);
    }
    
    my $output_name = $contig_desc . ".png";
    open(my $output, ">", "img/$output_name") or die ("could not create, $!\n");
    print $output $panel->png;
}


