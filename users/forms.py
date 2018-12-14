from django import forms
from django.contrib.auth.models import User as DjangoUser


class DjangoUserForm(forms.ModelForm):
    """Form to change Django User settings"""

    class Meta:
        model = DjangoUser
        fields = ['first_name', 'last_name', 'email']
