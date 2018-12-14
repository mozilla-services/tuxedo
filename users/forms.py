from django import forms
from django.contrib.auth.models import User as DjangoUser

from .models import UserProfile


class DjangoUserForm(forms.ModelForm):
    """Form to change Django User settings"""

    class Meta:
        model = DjangoUser
        fields = ['first_name', 'last_name', 'email']


class UserProfileForm(forms.ModelForm):
    """Form to change additional user profile data"""

    class Meta:
        model = UserProfile
        fields = ['address', 'phone_number', 'ircnick']
