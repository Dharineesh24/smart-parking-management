from django import forms
from django.contrib.auth.models import User
from .models import AdminProfile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['phone', 'profile_photo']