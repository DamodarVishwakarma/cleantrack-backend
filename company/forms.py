from django.forms import ModelForm
from django import forms
from company.models import Company


class CompanyForm(ModelForm):
    name = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Company Name'
    })))
    street = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Street'
    })))
    city = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'City'
    })))
    state = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'State'
    })))
    zip_code = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Zip Code'
    })))

    class Meta:
        model = Company
        fields = ['name','street','city','state','zip_code','company_type','company_status']
