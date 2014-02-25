from django import forms
from django.forms import ModelForm
from mainsite.models import *
from django.contrib.auth.models import User
from django.forms.models import BaseFormSet, inlineformset_factory

# For Cosmid-End Tag add
class CosmidForm(ModelForm):
    class Meta:
        model = Cosmid

# For Cosmid-End Tag add    
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

# For ORF-Contig add
class ContigORFJoinForm(ModelForm):
    class Meta:
        model = Contig_ORF_Join
        exclude = ('db_generated', 'orf', 'start', 'stop')

# For subclone search
class SubcloneForm(ModelForm):
    class Meta:
        model = Subclone

# For orf search
class OrfSearchForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('orf_sequence', 'contig',)

# For subclone assay search
class SubcloneAssayForm(ModelForm):
    class Meta:
        model = Subclone_Assay

# For cosmid assay search
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

# For Contig-Pool add
class UploadContigsForm(forms.Form):
    fasta_file = forms.FileField(label='Select a FASTA file', help_text=' ')
    
