from django import forms
from django.forms import ModelForm, RadioSelect, ChoiceField
from mainsite.models import *
from django.forms import widgets
from django.contrib.auth.models import User
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
    
#For ORF-Contig add
class ORFForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('contig', 'id',)
        

#For ORF-Contig add
class ContigORFJoinForm(ModelForm):
    class Meta:
        model = Contig_ORF_Join
        exclude = ('orf', 'start', 'stop', 'predicted', 'prediction_score')
        labels = {
            'complement': ('*ORF on Contig complement?'),
        }

#For Subclone search
class SubcloneForm(ModelForm):
    class Meta:
        model = Subclone

#For ORF Search
class OrfSearchForm(ModelForm):
    class Meta:
        model = ORF
        fields = ['annotation', 'id'] #need to fix this so ID shows in form. it doesnt work as is.

#For subclone assay search
class SubcloneAssayForm(ModelForm):
    class Meta:
        model = Subclone_Assay

#For cosmid assay search
class CosmidAssayForm(ModelForm):
    class Meta:
        model = Cosmid_Assay

#For contig search
class ContigSearchForm(ModelForm):
    class Meta:
        model = Contig
        exclude = ('contig_sequence', 'blast_hit_accession', 'cosmid')
        
#Change user preferences    
class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ('last_login', 'is_superuser', 'username', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions',)
        
# For Contig-Pool add
class ContigForm(ModelForm):
    class Meta:
        model = Contig
        exclude = ('contig_name', 'contig_sequence', 'cosmid', 'contig_accession', 'blast_hit_accession')

# For Contig-Pool add
class UploadContigsForm(forms.Form):
    fasta_file = forms.FileField(label='Select a FASTA file', help_text=' ')

#BLAST Form
class BlastForm(forms.Form):
    sequence = forms.CharField(label='Sequence', widget=forms.Textarea)
    expect_threshold = forms.ChoiceField(label='E-value Cut-Off', choices=[(str(x), x) for x in (10, 1, 0.1, 0.01, 0.001, 0.0001)], initial=0.01)
    word_size = forms.ChoiceField(label='Word Size', choices=[(str(x), x) for x in range(7, 20)], initial=11)
    match_score = forms.ChoiceField(label='Nucleotide Match Score', choices=[(str(x), x) for x in (1,2,4)], initial=2)
    mismatch_score = forms.ChoiceField(label='Nucleotide Mismatch Score', choices=[(str(x), x) for x in (-1,-2,-3,-4,-5)], initial=-3)
    gap_open_penalty = forms.ChoiceField(label='Gap Open Penalty', choices=[(str(x), x) for x in (0,2,3,4,5,6)], initial=5)
    gap_extension_penalty = forms.ChoiceField(label='Gap Extension Penalty', choices=[(str(x), x) for x in (2,3,4)], initial=2)

#All Search form
class AllSearchForm(forms.Form):
    query = forms.CharField(label='Keywords', required=True)