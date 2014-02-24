from django import forms
from django.forms import ModelForm
from mainsite.models import *
from django.forms.models import BaseFormSet, inlineformset_factory

# For Cosmid-End Tag add

class CosmidForm(ModelForm):
    class Meta:
        model = Cosmid
    
EndTagFormSet = inlineformset_factory(Cosmid, 
    End_Tag, 
    can_delete=False,
    extra=2,
    form=CosmidForm)
    
# For ORF-Contig add

class ORFForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('contig', 'id',)

class ContigORFJoinForm(ModelForm):
    class Meta:
        model = Contig_ORF_Join
        exclude = ('db_generated', 'orf', 'start', 'stop')
        
# For Contig-Pool add

class ContigForm(ModelForm):
    class Meta:
        model = Contig

class UploadContigsForm(forms.Form):
    fasta_file = forms.FileField(label='Select a FASTA file', help_text=' ')

        
