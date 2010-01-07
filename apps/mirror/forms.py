from django import forms
from models import Product

class UptakeForm(forms.Form):
    p = forms.ModelMultipleChoiceField(
        queryset=Product.objects.order_by('name'),
        label='Products')

