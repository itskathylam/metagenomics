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

    #I dont know where these came from or where the are supposed to go. Sorry, I messed up the merge. -Phil
    #model = End_Tag
    #exclude = ('cosmid',)
    
# For ORF-Contig add

class ORFForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('contig', 'id',)


class ContigORFJoinForm(ModelForm):
    class Meta:
        model = Contig_ORF_Join
        exclude = ('db_generated', 'orf', 'start', 'stop')


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
        exclude = ('last_login', 'is_superuser', 'username', 'is_staff', 'is_active', 'date_joined', 'group', 'permission',)
 
 
# For Contig-Pool add

class ContigForm(ModelForm):
    class Meta:
        model = Contig
        exclude = ('contig_name', 'contig_sequence', 'cosmid', 'contig_accession')


class UploadContigsForm(forms.Form):
    fasta_file = forms.FileField(label='Select a FASTA file', help_text=' ')
    

#BLAST Sequence Form
class BlastForm(forms.Form):
    sequence = forms.CharField(label='sequence', required=True)
    maxr = forms.CharField()
    expectthreshold = forms.CharField()
    wordsize = forms.CharField()
    mmscore = forms.Select()
    gapc = forms.Select()

