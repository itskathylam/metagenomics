from django.forms import ModelForm
from mainsite.models import *

class CosmidForm(ModelForm):
    class Meta:
        model = Cosmid

class EndTagForm(ModelForm):
    class Meta:
        model = End_Tag
        exclude = ('cosmid',)