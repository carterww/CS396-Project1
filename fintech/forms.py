from django.forms import ModelForm, ClearableFileInput
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import DocumentFile

class CreateUserForm(UserCreationForm) :
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class FileForm(forms.Form) :
    content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
