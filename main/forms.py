from django.contrib.auth.models import User
from django.forms import ModelForm


class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
