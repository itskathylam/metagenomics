from django.forms import ModelForm
from mainsite.models import *
from django.forms.models import BaseFormSet, inlineformset_factory

class CosmidForm(ModelForm):
    class Meta:
        model = Cosmid

#class BaseEndTagFormSet(BaseFormSet):
#    def clean(self):
#        sequences = []
#        for form in self.forms:
#            seq = form.cleaned_data['end_tag_sequence']
#            seq.strip()
#            sequences.append(seq)
    

EndTagFormSet = inlineformset_factory(Cosmid, 
    End_Tag, 
    can_delete=False,
    extra=2,
    form=CosmidForm)
    #formset=BaseEndTagFormSet,
    

class ORFForm(ModelForm):
    class Meta:
        model = ORF
        exclude = ('contig', 'id',)

class ContigORFJoinForm(ModelForm):
    class Meta:
        model = Contig_ORF_Join
        exclude = ('db_generated', 'orf', 'start', 'stop')
        
