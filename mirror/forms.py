from django import forms
from .models import Product, ProductAlias


class UptakeForm(forms.Form):
    p = forms.ModelMultipleChoiceField(
        queryset=Product.objects.order_by('name'), label='Products')


class ProductAliasForm(forms.ModelForm):

    E_ALIAS_GENERAL_VALIDATION_ERROR = 101
    E_ALIAS_REQUIRED = 102
    E_PRODUCT_DOESNT_EXIST = 103
    E_ALIAS_PRODUCT_MATCH = 104
    E_RELATED_NAME_REQUIRED = 105

    class Meta:
        model = ProductAlias
        fields = ['alias', 'related_product']

    def clean_alias(self):
        if Product.objects.filter(name=self.cleaned_data['alias']).exists():
            raise forms.ValidationError(
                'Your alias cannot share the same name as an existing product!'
            )
        return self.cleaned_data['alias']

    def clean_related_product(self):
        if not Product.objects.filter(
                name=self.cleaned_data['related_product']).exists():
            raise forms.ValidationError('The product you entered was invalid')
        return self.cleaned_data['related_product']
