from django import forms
from django.forms import ModelForm
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
    
# For ORF-Contig add

class ORFForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('contig', 'id',)


class ContigORFJoinForm(ModelForm):
    class Meta:
        model = Contig_ORF_Join
        exclude = ('orf', 'start', 'stop', 'predicted', 'prediction_score')


class SubcloneForm(ModelForm):
    class Meta:
        model = Subclone

#For ORF Search
class OrfSearchForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('orf_sequence', 'contig',)

class SubcloneAssayForm(ModelForm):
    class Meta:
        model = Subclone_Assay

class CosmidAssayForm(ModelForm):
    class Meta:
        model = Cosmid_Assay

class SubcloneCosmidForm(ModelForm):
    class Meta:
        model = Cosmid_Assay
    
    
class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ('last_login', 'is_superuser', 'username', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions',)
        
 
# For Contig-Pool add
class ContigForm(ModelForm):
    class Meta:
        model = Contig
        exclude = ('contig_name', 'contig_sequence', 'cosmid', 'contig_accession')
        pool = forms.Select()
        #pool = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'get_details();'}))

class UploadContigsForm(forms.Form):
    fasta_file = forms.FileField(label='Select a FASTA file', help_text=' ')
    

#BLAST Sequence Form
class BlastForm(forms.Form):
    sequence = forms.CharField(label='Sequence', required=True)
    maxr = forms.CharField(label='Number of returned hits')
    expectthreshold = forms.CharField(label='E-value cut-off')
    wordsize = forms.CharField(label='Word size')
    mmscore = forms.Select()
    gapc = forms.Select()

#All Search form
class AllSearchForm(forms.Form):
    query = forms.CharField(label='Keywords', required=True)
