from django.forms import ModelForm
from django import forms
from .models import User
from company.models import Company
from digitalplatformbackend.constants import user_constants
from digitalplatformbackend.constants import company_constants


class UserForm(ModelForm):
    first_name = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'text',
        'placeholder': 'First Name'
    })), required=False)
    last_name = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'text',
        'placeholder': 'Last Name'
    })), required=False)
    email = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'email',
        'placeholder': 'Email'
    })))
    phone = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'text',
        'placeholder': 'Phone Number'
    })))
    # company = forms.ModelChoiceField(queryset=Company.objects.all(), widget=(forms.Select(attrs={
    #     'class': 'form-control col-sm-9',
    #     'type': 'text',
    #     'placeholder': 'Choose Company',
    # })), required=False)
    street = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'text',
        'placeholder': 'Street'
    })), required=False)
    city = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'text',
        'placeholder': 'City'
    })), required=False)
    state = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'text',
        'placeholder': 'State'
    })), required=False)
    zip_code = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control col-sm-9',
        'type': 'text',
        'placeholder': 'Zip Code'
    })), required=False)

    class Meta:
        model = User
        fields = ['company', 'street', 'city', 'state', 'zip_code', 'email', 'phone', 'user_type',
                  'approved_by_company_admin', 'approved_by_super_admin', 'first_name', 'last_name',
                  'password', 'is_staff', 'is_superuser', 'is_active','allow_to_send_mail',]


class LoginForm(ModelForm):
    email = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'email',
        'placeholder': 'example@email.com'
    })))
    password = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'password',
        'placeholder': 'password'
    })))

    class Meta:
        model = User
        fields = ['email', 'password']
