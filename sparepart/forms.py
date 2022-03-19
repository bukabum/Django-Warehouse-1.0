from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.postgres import fields as django_fields
from django.forms import ModelForm, widgets
from django.forms import ClearableFileInput
from pathlib import Path
from django.utils.deconstruct import deconstructible

from django.core.validators import MaxValueValidator
from django.utils.translation import ugettext as _

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator

#######################   Withdraw   ##########################

class SparePartForm(forms.ModelForm):
    name = forms.CharField(required=True, error_messages = {'required':_("Nama Barang")}, min_length=1, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'id':'name', 'placeholder': _('Nama Barang')}))
    #product_code = forms.CharField(required=False, min_length=10, max_length=20, widget=forms.NumberInput(attrs={'title':'Must be 10 - 18 digit number', 'pattern':'\d{10}|\d{11}|\d{12}|\d{13}|\d{14}|\d{15}|\d{16}|\d{17}|\d{18}', 'class': 'form-control', 'id':'account_number', 'placeholder': _('Account Number')}))
    #description = forms.CharField(required=True, min_length=10, max_length=200, widget=forms.NumberInput(attrs={'title':'Must be 10 - 15 digit number', 'pattern':'\d{10}|\d{11}|\d{12}|\d{13}|\d{14}|\d{15}', 'class': 'form-control', 'id':'ovo_phone', 'placeholder': _('Phone Number')}))
    #stock = forms.CharField(required=True, min_length=1, max_length=15, widget=forms.NumberInput(attrs={'title':'Must be 10 - 15 digit number', 'pattern':'\d{1}|\d{2}|\d{3}|\d{4}|\d{5}|\d{6}|\d{7}|\d{8}|\d{9}|\d{10}|\d{11}|\d{12}|\d{13}|\d{14}|\d{15}', 'class': 'form-control', 'id':'gopay_phone', 'placeholder': _('Phone Number')}))
    #price = forms.CharField(required=True, min_length=1, max_length=15, widget=forms.NumberInput(attrs={'title':'Must be 10 - 15 digit number', 'pattern':'\d{1}|\d{2}|\d{3}|\d{4}|\d{5}|\d{6}|\d{7}|\d{8}|\d{9}|\d{10}|\d{11}|\d{12}|\d{13}|\d{14}|\d{15}', 'class': 'form-control', 'id':'gopay_phone', 'placeholder': _('Phone Number')}))
    product_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'id':'name', 'placeholder': _('Kode Produk')}))
    description = forms.CharField(required=True, error_messages = {'required':_("Deskripsi Barang")}, min_length=1, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'id':'name', 'placeholder': _('Deskripsi Barang')}))
    stock = forms.CharField(required=True, min_length=1, max_length=15, widget=forms.NumberInput(attrs={'title':'Wajid di isi, hanya angka', 'pattern':'\d{1}|\d{2}|\d{3}|\d{4}|\d{5}', 'class': 'form-control', 'id':'gopay_phone', 'placeholder': _('Jumlah Stock')}))
    price = forms.CharField(required=True, min_length=1, max_length=15, widget=forms.NumberInput(attrs={'title':'Wajid di isi, hanya angka', 'pattern':'\d{1}|\d{2}|\d{3}|\d{4}|\d{5}|\d{6}|\d{7}|\d{8}|\d{9}|\d{10}|\d{11}|\d{12}|\d{13}|\d{14}|\d{15}', 'class': 'form-control', 'id':'gopay_phone', 'placeholder': _('Harga Barang')}))
    class Meta:
        exclude = ['qrcode', 'person_responsible', 'person_who_update', 'first_stock']
        model = SparePart
        fields = '__all__'
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(SparePartForm,self).__init__(*args, **kwargs)
        self.fields['name'].label = "Nama Barang"
        self.fields['product_code'].label = "Kode Produk"
        self.fields['description'].label = "Deskripsi"
        self.fields['stock'].label = "Jumlah Stock"
        self.fields['price'].label = "Harga"
        self.fields['image'].label = "Gambar"
