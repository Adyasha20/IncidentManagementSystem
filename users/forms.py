from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only reporters can self-register; agents/admins created by superuser
        self.fields['role'].choices = [('REPORTER', 'Reporter')]
        self.fields['role'].initial = 'REPORTER'
