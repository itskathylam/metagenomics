from django.forms import ModelForm

class CosmidForm(forms.ModelForm):
    class Meta:
        model = Cosmid

class EndTagForm(forms.ModelForm):
    class Meta:
        model = End_Tag
        exclude = ('cosmid',)