from django.forms import ModelForm
from mainsite.models import *
from django.contrib.auth.models import User


class CosmidForm(ModelForm):
    class Meta:
        model = Cosmid

class EndTagForm(ModelForm):
    class Meta:
        model = End_Tag
        exclude = ('cosmid',)

class SubcloneForm(ModelForm):
    class Meta:
        model = Subclone
        
class UserForm(ModelForm):
    class Meta:
        model = User
        exclude = ('last_login', 'is_superuser', 'username', 'is_staff', 'is_active', 'date_joined', 'group', 'permission',)