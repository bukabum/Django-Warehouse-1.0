import django_filters
from django_filters.filters import RangeFilter, DateFilter, DateRangeFilter
from .models import *
from django.db.models import Q
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _
from django_filters.widgets import RangeWidget
from django_filters.rest_framework import FilterSet
from django_filters.widgets import CSVWidget

class RestSparePartFilter(django_filters.rest_framework.FilterSet):
    
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label=(_('Kategori')), empty_label=(_('Kategori Produk')))
    name = django_filters.CharFilter(method='filter_q', label=(_('Nama Produk')), widget=TextInput(attrs={'placeholder': _('Nama Produk'), 'class': 'search_title'}))
    product_code = django_filters.CharFilter(method='filter_code', label=(_('Kode Produk')), widget=TextInput(attrs={'placeholder': _('Kode Produk'), 'class': 'search_code'}))
    price = django_filters.RangeFilter(label=(_('Harga')))

    class Meta:
        model = SparePart
        #fields = ['processtime', 'revision', 'category', 'title', 'price']
        fields = ['name', 'category', 'price', 'product_code']

    def filter_q(self, qs, name, value):
        return qs.filter(
            Q(name__icontains=value) | Q(description__icontains=value) | Q(category__name__icontains=value) | Q(product_code__icontains=value)
        )

    def filter_code(self, qs, name, value):
        return qs.filter(
            Q(product_code__icontains=value)
        )


class SparePartFilter(django_filters.FilterSet):
    
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label=(_('Kategori')), empty_label=(_('Kategori Produk')))
    name = django_filters.CharFilter(method='filter_q', label=(_('Nama Produk')), widget=TextInput(attrs={'placeholder': _('Nama Produk'), 'class': 'search_title'}))
    product_code = django_filters.CharFilter(method='filter_code', label=(_('Kode Produk')), widget=TextInput(attrs={'placeholder': _('Kode Produk'), 'class': 'search_code'}))
    price = django_filters.RangeFilter(label=(_('Harga')))

    class Meta:
        model = SparePart
        #fields = ['processtime', 'revision', 'category', 'title', 'price']
        fields = ['name', 'category', 'price', 'product_code']

    def filter_q(self, qs, name, value):
        return qs.filter(
            Q(name__icontains=value) | Q(description__icontains=value) | Q(category__name__icontains=value) | Q(product_code__icontains=value)
        )

    def filter_code(self, qs, name, value):
        return qs.filter(
            Q(product_code__icontains=value)
        )

class RestStockFilter(django_filters.rest_framework.FilterSet):
    #start_date = DateFilter(field_name='date',lookup_expr=('gt'),) 
    #end_date = DateFilter(field_name='date',lookup_expr=('lt'))
    date_range = DateRangeFilter(field_name='date_added')
    date_added = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'type': 'date'}), label=(_('Tanggal')))

    class Meta:
        model = EnhanceInOutStock
        fields = ['date_added']

class StockFilter(django_filters.FilterSet):
    #start_date = DateFilter(field_name='date',lookup_expr=('gt'),) 
    #end_date = DateFilter(field_name='date',lookup_expr=('lt'))
    date_range = DateRangeFilter(field_name='date_added')
    date_added = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'type': 'date'}), label=(_('Tanggal')))

    class Meta:
        model = EnhanceInOutStock
        fields = ['date_added']

class RestOrderFilter(django_filters.rest_framework.FilterSet):
    
    total_amount = django_filters.RangeFilter(label=(_('Harga')))
    creation_date = django_filters.DateFromToRangeFilter(widget=RangeWidget(attrs={'type': 'date'}), label=(_('Tanggal Order')))
    paid = django_filters.BooleanFilter(field_name='paid')
    cancel = django_filters.BooleanFilter(field_name='cancel')
    retur = django_filters.BooleanFilter(field_name='retur')
    order_code = django_filters.CharFilter(method='filter_q', label=(_('Kode Barang')), widget=TextInput(attrs={'placeholder': _('Kode Barang'), 'class': 'search_title'}))

    class Meta:
        model = Order
        fields = ['paid', 'creation_date', 'cancel', 'retur', 'total_amount', 'order_code']

    def filter_q(self, qs, name, value):
        return qs.filter(
            Q(order_code__icontains=value)
        )

class OrderFilter(django_filters.FilterSet):
    
    total_amount = django_filters.RangeFilter(label=(_('Harga')))
    request_order = DateRangeFilter(field_name='request_order')
    paid = django_filters.BooleanFilter(field_name='paid')
    cancel = django_filters.BooleanFilter(field_name='cancel')
    retur = django_filters.BooleanFilter(field_name='retur')

    class Meta:
        model = Order
        fields = ['paid', 'request_order', 'cancel', 'retur', 'total_amount']

    def filter_q(self, qs, name, value):
        return qs.filter(
            Q(order_code__icontains=value)
        )

class RestCustomerFilter(django_filters.rest_framework.FilterSet):
    nama_pelanggan = django_filters.CharFilter(method='filter_nama', label=(_('Nama Pembeli')), widget=TextInput(attrs={'placeholder': _('Nama Pembeli'), 'class': 'search_buyer'}))
    alamat = django_filters.CharFilter(method='filter_alamat', label=(_('Alamat')), widget=TextInput(attrs={'placeholder': _('Alamat'), 'class': 'search_buyer'}))
    no_hp = django_filters.CharFilter(method='filter_no_hp', label=(_('No Hp')), widget=TextInput(attrs={'placeholder': _('No Hp'), 'class': 'search_buyer'}))
     
    class Meta:
        model = Customer
        fields = ['nama_pelanggan', 'alamat', 'no_hp']

    def filter_nama(self, qs, name, value):
        return qs.filter(
            Q(nama_pelanggan__icontains=value)
        )
    def filter_alamat(self, qs, name, value):
        return qs.filter(
            Q(alamat__icontains=value)
        )
    def filter_no_hp(self, qs, name, value):
        return qs.filter(
            Q(no_hp__icontains=value)
        )

class CustomerFilter(django_filters.FilterSet):
    nama_pelanggan = django_filters.CharFilter(method='filter_nama', label=(_('Nama Pembeli')), widget=TextInput(attrs={'placeholder': _('Nama Pembeli'), 'class': 'search_buyer'}))
    alamat = django_filters.CharFilter(method='filter_alamat', label=(_('Alamat')), widget=TextInput(attrs={'placeholder': _('Alamat'), 'class': 'search_buyer'}))
    no_hp = django_filters.CharFilter(method='filter_no_hp', label=(_('No Hp')), widget=TextInput(attrs={'placeholder': _('No Hp'), 'class': 'search_buyer'}))
     
    class Meta:
        model = Customer
        fields = ['nama_pelanggan', 'alamat', 'no_hp']

    def filter_nama(self, qs, name, value):
        return qs.filter(
            Q(nama_pelanggan__icontains=value)
        )
    def filter_alamat(self, qs, name, value):
        return qs.filter(
            Q(alamat__icontains=value)
        )
    def filter_no_hp(self, qs, name, value):
        return qs.filter(
            Q(no_hp__icontains=value)
        )

