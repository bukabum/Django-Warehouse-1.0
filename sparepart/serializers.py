from rest_framework import serializers 
from .models import *

class SparePartSerializer(serializers.ModelSerializer):

    class Meta:
        model = SparePart
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    parts = SparePartSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('parts',)

