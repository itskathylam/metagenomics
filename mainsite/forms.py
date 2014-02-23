from django.forms import ModelForm
from mainsite.models import *
from django.forms.models import inlineformset_factory

class CosmidForm(ModelForm):
    class Meta:
        model = Cosmid
        
EndTagFormSet = inlineformset_factory(Cosmid, 
    End_Tag, 
    can_delete=False,
    extra=2,
    form=CosmidForm)

class ORFForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('contig', 'id',)

class ContigORFJoinForm(ModelForm):
    class Meta:
        model = Contig_ORF_Join
        exclude = ('db_generated', 'orf', 'start', 'stop')
