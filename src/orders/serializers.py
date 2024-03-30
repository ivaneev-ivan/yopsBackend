from rest_framework import serializers
from .models import ServerLocation, Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('solar', 'user')


class ServerLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerLocation
        fields = '__all__'
