from django.forms import ModelForm
from django import forms
from .models import Order, Consignment, CollectionEntries, Remark
from company.models import Company
from user.models import User
from digitalplatformbackend.constants import company_constants, user_constants


class OrderForm(ModelForm):
    order_number = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Order Number'
    })),required=True)
    order_weight = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Weight in KG'
    })),required=True)
    collection_agency = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=company_constants.collection_agency), widget=(forms.Select(attrs={
            'class': 'form-control col-sm-9',
            'type': 'text',
        })), empty_label='Choose Company',required=True)
    disposal_agency = forms.ModelChoiceField(
        queryset=Company.objects.filter(company_type=company_constants.disposal_agency), widget=(forms.Select(attrs={
            'class': 'form-control col-sm-9',
            'type': 'text'
        })), empty_label='Chose Company',required=True)
    customer = forms.ModelChoiceField(queryset=User.objects.filter(user_type=user_constants.Customer),
                                      widget=(forms.Select(attrs={
                                          'class': 'form-control col-sm-9',
                                          'type': 'text'
                                      })), empty_label='Choose User',required=True)

    class Meta:
        model = Order
        fields = '__all__'


class ConsignmentForm(ModelForm):
    order_number = forms.ModelChoiceField(
        queryset=Order.objects.all(), widget=(forms.Select(attrs={
            'class': 'form-control col-sm-9',
            'type': 'text'
        })), empty_label='Choose Order',required=True)
    consignment_id = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Consignment Number'
    })),required=True)
    vehicle_number = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Vehicle Number'
    })),required=True)

    class Meta:
        model = Consignment
        fields = '__all__'


class CollectionEntriesForm(ModelForm):
    consignment = forms.ModelChoiceField(
        queryset=Consignment.objects.all(), widget=(forms.Select(attrs={
            'class': 'form-control col-sm-9',
            'type': 'text',
        })), empty_label='Choose Consignment',required=True)
    company = forms.ModelChoiceField(queryset=Company.objects.filter(company_type=company_constants.collection_agency),
                                     widget=(forms.Select(attrs={
                                         'class': 'form-control col-sm-9',
                                         'type': 'text'
                                     })), empty_label='Choose Company',required=True)
    collected_by = forms.ModelChoiceField(queryset=User.objects.filter(user_type=user_constants.Collection_Agent),
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
    })),required=False)
    longitude = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'autocomplete': 'False'
    })),required=False)
    vehicle_number = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Vehicle Number'
    })))
    weight = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Weight'
    })),required=True)
    license_plate_no = forms.CharField(widget=(forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'License Plate Number'
    })), required=False)

    class Meta:
        model = CollectionEntries
        fields = ['consignment', 'company', 'collected_by', 'city', 'latitude',
                  'longitude', 'vehicle_number', 'empty_vehicle_img', 'loaded_vehicle_img', 'lr_copy_img',
                  'vehicle_number_img', 'delivery_challan_img', 'e_way_bill_img', 'weighment_slip_img',
                  'weight', 'status', 'license_plate_no', 'manual_entry'
                  ]


class CollectionReviewForm(ModelForm):

    class Meta:
        model = CollectionEntries
        fields = ['status',]


class RemarkForm(ModelForm):
    remark = forms.CharField(widget=forms.Textarea(attrs={
        "rows":'5',
        'class': 'form-control',
    }), required=False)

    class Meta:
        model = Remark
        fields = ['remark',]
