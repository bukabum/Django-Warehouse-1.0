from sparepart.models import * 
from rest_framework import serializers

class SparePartSerializer(serializers.ModelSerializer):

    class Meta:
        model = SparePart
        fields = ['pk', 'name', 'first_stock', 'product_code', 'description', 'stock', 'price', 'promo_price', 'image', 'qrcode', 'date_added', 'update_date', 'category', 'person_responsible', 'person_responsible_for_update']

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['category_id', 'name', 'slug', 'create_at', 'update_at', 'code']

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['pk', 'nama_pelanggan', 'catatan', 'alamat', 'Kecamatan', 'kota', 'provinsi', 'no_hp', 'person_responsible', 'creation_date']

class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['preorder', 'order', 'pk', 'parts', 'person_responsible', 'creation_date', 'discount', 'quantity', 'internal_note', 'external_note', 'request_order', 'paid', 'receipt', 'total_price', 'use_discaunt']
        depth = 2

class ReceiptOrderItemSeializer(serializers.ModelSerializer):
    parts = SparePartSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('parts',)

class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(read_only=True, many=True)
    class Meta:
        model = Order
        fields = ['orderitem_set', 'pk', 'request_order', 'paid', 'person_responsible', 'creation_date', 'discount', 'total_amount', 'order_code', 'cancel', 'cancel_reason', 'retur', 'retur_reason', 'paid_proof', 'customer', 'cancel_date', 'paid_date', 'retur_date', 'note']
        depth = 1

class BaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['pk', 'request_order', 'paid', 'person_responsible', 'creation_date', 'discount', 'total_amount', 'order_code', 'cancel', 'cancel_reason', 'retur', 'retur_reason', 'paid_proof', 'customer', 'cancel_date', 'paid_date', 'retur_date', 'note']
        depth = 1

class SingleOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['pk', 'request_order', 'paid', 'person_responsible', 'creation_date', 'discount', 'total_amount', 'order_code', 'cancel', 'cancel_reason', 'retur', 'retur_reason', 'paid_proof', 'customer', 'cancel_date', 'paid_date', 'retur_date', 'note']
        depth = 1

    def to_representation(self, instance):
        if instance.paid == True:
            representation = super().to_representation(instance)
            paid_proof = {
                "url": representation.pop("paid_proof"),
                "size": instance.paid_proof.size,
                "name": instance.paid_proof.name,
            }
            representation['paid_proof'] = paid_proof
            return representation
        else: 
            representation = super().to_representation(instance)
            paid_proof = {
                "url": '',
                "size": '',
                "name": '',
            }
            representation['paid_proof'] = ''
            return representation

class EnhanceInOutStockSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnhanceInOutStock
        fields = ['pk', 'stockin', 'stockout', 'stock', 'description', 'date_added', 'parts', 'person_responsible']

class LogoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logo
        fields = ['pk', 'logo']

class PromotionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Promotion
        fields = ['pk', 'promotion']

class DownPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = DownPayment
        fields = ['pk', 'proof', 'order', 'nilai', 'note', 'creation_date']

    def to_representation(self, instance):
        if instance.proof:
            representation = super().to_representation(instance)
            proof = {
                "url": representation.pop("proof"),
                "size": instance.proof.size,
                "name": instance.proof.name,
            }
            representation['proof'] = proof
            return representation

