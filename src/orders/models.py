import json
from django.db import models
from django.conf import settings


class ServerLocation(models.Model):
    """Локация сервера"""
    title = models.CharField("Название локации", max_length=100, unique=True)
    solar = models.PositiveSmallIntegerField('Цена в rub за месяц пользования')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Локация сервера'
        verbose_name_plural = 'Локации серверов'

class Payment(models.Model):
    is_paid = models.BooleanField(
        default=False
    )
    price = models.PositiveIntegerField(
        blank=False,
        null=False
    )
    payment_url = models.TextField(
        blank=True,
        null=True
    )
    payment_id = models.CharField(
        max_length=200
    )

    def __str__(self):
        return f'{self.price}'

    @property
    def update_payment(self):
        # self.is_paid = not self.is_paid
        self.is_paid = True
        self.save()
        order = Order.objects.get(payment_id=self.id)
        order.status = 2
        order.save()

    class Meta:
        db_table = 'payments'


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Сформирован'),
        ('payed', 'Оплачен'),
        ('working', 'В обработке'),
        ('done', 'Выполнен'),
    ]
    count_configs = models.PositiveSmallIntegerField('Количество конфигов')
    is_own_server = models.BooleanField('Создавать новый сервер')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.ForeignKey(ServerLocation, on_delete=models.PROTECT)
    solar = models.PositiveIntegerField('Стоимость заказа')
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True
    )
    services = models.CharField(max_length=100, default='["vpn"]')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def set_services(self, services):
        self.services = json.dumps(services)
    def get_services(self):
        return json.loads(self.services)
    def save(self, *args, **kwargs):
        if self.is_own_server:
            self.solar = self.location.solar + self.count_configs * 25
        else:
            self.solar = self.count_configs * 100
        super(Order, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderOutline(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    apiUrl = models.TextField('Ссылка на api')
    certSha256 = models.TextField('Токен доступа к manager')
    update_time = models.DateTimeField('Дата обновления', auto_now=True)
    create_time = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        db_table = 'order_outlines'

class ConfigKey(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=150)
    password = models.CharField(max_length=100)
    port = models.PositiveIntegerField()
    method = models.CharField(max_length=50)
    accessUrl = models.TextField()

    def __str__(self):
        return f"Order {self.order} {self.accessUrl[:5]}"

    class Meta:
        db_table = "configs_key"
