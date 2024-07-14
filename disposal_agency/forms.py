from django.forms import ModelForm
from django import forms
from company.models import Company
from .models import Consignment

from user.models import User
from digitalplatformbackend.constants import company_constants, user_constants
from .models import DisposalEntries


class DisposalEntriesForm(ModelForm):
    consignment = forms.ModelChoiceField(
        queryset=Consignment.objects.all(), widget=(forms.Select(attrs={
            'class': 'form-control col-sm-9',
            'type': 'text',
        })), empty_label='Choose Consignment',required=True)
    company = forms.ModelChoiceField(queryset=Company.objects.filter(company_type=company_constants.disposal_agency),
                                     widget=(forms.Select(attrs={
                                         'class': 'form-control col-sm-9',
                                         'type': 'text'
                                     })), empty_label='Choose Company',required=True)
    collected_by = forms.ModelChoiceField(queryset=User.objects.filter(user_type=user_constants.Disposal_Agent),
                                          widget=(forms.Select(attrs={
                                              'class': 'form-control col-sm-9',
                                              'type': 'text'
                                          })), empty_label='Choose User',required=True)

    city = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'City'
    })),required=True)
    latitude = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'autocomplete': 'False'
    })))
    longitude = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'autocomplete': 'False'
    })))
    vehicle_number = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Vehicle Number'
    })),required=True)
    weight = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Weight'
    })),required=True)

    class Meta:
        model = DisposalEntries
        fields = '__all__'


class DisposalReviewForm(ModelForm):
    class Meta:
        model = DisposalEntries
        fields = ['disposal_status', ]
