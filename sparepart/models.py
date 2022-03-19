import qrcode

from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords
from warehouse.storage_backends import PublicMediaStorage, PrivateMediaStorage
import datetime

# Create your models here.
class Category(models.Model):
    category_id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=200, unique=True, default=None)
    create_at=models.DateTimeField(auto_now_add=True)
    update_at=models.DateTimeField(auto_now=True)
    code = models.CharField(max_length=255, unique=True, default=None)
    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']
    

class SparePart(models.Model):
    first_stock = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length = 200)
    product_code = models.CharField(max_length = 200, blank=True, null=True)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    price = models.PositiveBigIntegerField()
    promo_price = models.PositiveBigIntegerField(default=0, null=True, blank=True)
    image = models.ImageField()
    qrcode = models.ImageField(blank=True, null=True)
    #image = models.ImageField(storage=PublicMediaStorage())
    #qrcode = models.ImageField(blank=True, null=True)
    qrcode_s3 = models.ImageField(blank=True, null=True, storage=PublicMediaStorage())
    date_added = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    person_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="username")
    person_responsible_for_update = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="person_who_update", on_delete=models.CASCADE, to_field="username", blank=True, null=True)
    #history = HistoricalRecords()

    def __str__(self):
        return self.name

class StockIn(models.Model):
    stockin = models.PositiveIntegerField()
    description = models.TextField()
    date_added = models.DateTimeField(blank=True, null=True)
    parts = models.ForeignKey(SparePart,on_delete=models.CASCADE, default=None, null=True, blank=True)
    person_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="username")

class StockOut(models.Model):
    stockout = models.PositiveIntegerField()
    description = models.TextField()
    date_added = models.DateTimeField(blank=True, null=True)
    parts = models.ForeignKey(SparePart,on_delete=models.CASCADE, default=None, null=True, blank=True)
    person_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="username")

class EnhanceInOutStock(models.Model):
    stockin = models.PositiveIntegerField()
    stockout = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()
    date_added = models.DateTimeField(blank=True, null=True)
    parts = models.ForeignKey(SparePart,on_delete=models.CASCADE, default=None, null=True, blank=True)
    person_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="username")

    #def __str__(self):
        #return self.parts.product_code

class Customer(models.Model):
    nama_pelanggan = models.CharField(max_length = 255)
    catatan = models.CharField(max_length = 255, blank=True, null=True)
    alamat = models.CharField(max_length = 255)
    Kecamatan = models.CharField(max_length = 255, default=None, blank=True, null=True)
    kota = models.CharField(max_length = 255, default=None, blank=True, null=True)
    provinsi = models.CharField(max_length = 255, default=None, blank=True, null=True)
    no_hp = models.PositiveBigIntegerField(default=0)
    person_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="username", blank=True, null=True)
    creation_date = models.DateTimeField(blank=True, null=True)

class Order(models.Model):
    request_order = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    person_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="username")
    creation_date = models.DateTimeField()
    discount = models.PositiveIntegerField(default=0)
    total_amount = models.PositiveBigIntegerField(default=0)
    order_code = models.PositiveBigIntegerField(default=0)
    cancel = models.BooleanField(default=False)
    cancel_reason = models.TextField(blank=True, null=True)
    retur = models.BooleanField(default=False)
    retur_reason = models.TextField(blank=True, null=True)
    #paid_proof = models.ImageField(storage=PublicMediaStorage(), blank=True, null=True)
    paid_proof = models.ImageField(blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=None, null=True, blank=True)
    cancel_date = models.DateTimeField(blank=True, null=True)
    retur_date = models.DateTimeField(blank=True, null=True)
    paid_date = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

class DownPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    proof = models.ImageField()
    nilai = models.PositiveBigIntegerField(default=0)
    note = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField()
    delete_reason = models.TextField(blank=True, null=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    parts = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    person_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, to_field="username")
    creation_date = models.DateTimeField()
    discount = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    internal_note = models.CharField(max_length = 255, blank=True, null=True)
    external_note = models.CharField(max_length = 255, blank=True, null=True)
    request_order = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    receipt = models.JSONField(blank=True, null=True)
    total_price = models.PositiveBigIntegerField(default=0)
    use_discaunt = models.BooleanField(default=False)
    preorder = models.BooleanField(default=False)
    preorder_amount = models.PositiveBigIntegerField(default=0)
    
class Logo(models.Model):
    #logo = models.ImageField(storage=PublicMediaStorage(), blank=True, null=True)
    logo = models.ImageField(blank=True, null=True)

class Promotion(models.Model):
    created_datetime = models.DateTimeField(default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    #promotion = models.ImageField(storage=PublicMediaStorage(), blank=True, null=True)
    promotion = models.ImageField(blank=True, null=True)

