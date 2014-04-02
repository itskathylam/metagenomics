#!/usr/bin/perl
use warnings;
use strict;
use Data::Dumper;
#
use Tk;



# Creates a MainWindow object (i.e. JFrame)
my $w = MainWindow->new;

# Container information: size of the window
$w->geometry("600x50");
# Title at the top of the page
$w->title("The Chosen One");
# Makes a frame/panel to work in.  However, it is possible to add components directly to $w
# Layout is made using
#   ->pack(-side=>'top')
my $frame1 = $w->Frame()->pack(-side=>'top');
# To the frame, add in a label (i.e. JLabel)
$frame1->Label(-text => "Original Sequence")->pack(-side => 'left');
# Adds a textbox, i.e. JTextBox and returns the value in it
# 'sunken' makes it look lowered down, 'raised' pops it out
my $old_seq = $frame1->Entry(-width => '15', -relief => 'sunken')->pack(-side => 'left');
# Adds a button and returns the status of the button
my $button = $frame1->Button(-text => "Clean Up",
                             -command => \&clean_up)->pack(-side => "left");
$frame1 -> Label(-text => "New Sequence") ->pack(-side => 'left');
my $new_seq = $frame1->Entry(-width => '15',
                             -relief => 'sunken')->pack(-side => 'left');
#Prevents entry into new-seq textbox
$new_seq->configure(-state=>'disabled');

print Dumper($button);
# 
MainLoop();

sub clean_up{
    my $seq = $old_seq->get();
    $seq =~ s/[^acgt]/x/ig;
    $new_seq->configure(-state=>'normal');
    $new_seq->delete(0,'end');
    $new_seq->insert('end', $seq);
    $new_seq->configure(-state=>'disabled');
}