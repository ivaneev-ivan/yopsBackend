import json
from rest_framework import serializers
from .models import ServerLocation, Order, ConfigKey
from .models import Payment as PaymentModel
from yookassa import Payment
from django.conf import settings


class OrderSerializer(serializers.ModelSerializer):
    payment_url = serializers.CharField(source='payment.payment_url', read_only=True)
    is_payed = serializers.BooleanField(source='payment.is_paid', read_only=True)

    def create(self, validated_data):
        order = Order.objects.create(
            user=validated_data['user'],
            location=validated_data['location'],
            count_configs=validated_data['count_configs'],
            is_own_server=validated_data['is_own_server']
        )
        payment = PaymentModel.objects.create(
            price=order.solar,
        )
        yookassa_payment = Payment.create({
            "amount": {
                "value": str(payment.price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"{settings.REDIRECT_URL}{order.id}"
            },
            "capture": True,
            "description": f"Заказ #{order.id}"
        }, payment.id)
        payment.payment_id = yookassa_payment.id
        payment.payment_url = json.loads(yookassa_payment.json())["confirmation"]["confirmation_url"]
        payment.save()
        order.payment_id = payment.id
        order.save()
        return order

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('solar', 'user')


class ServerLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerLocation
        fields = '__all__'


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigKey
        fields = ('order', 'name', 'password', 'port', 'method', 'accessUrl')
