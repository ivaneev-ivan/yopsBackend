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


class Order(models.Model):
    count_configs = models.PositiveSmallIntegerField('Количество конфигов')
    is_own_server = models.BooleanField('Создавать новый сервер')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.ForeignKey(ServerLocation, on_delete=models.PROTECT)
    solar = models.PositiveIntegerField('Стоимость заказа')

    def save(self, *args, **kwargs):
        if self.is_own_server:
            self.solar = self.location.solar + self.count_configs * 25
        else:
            self.solar = self.count_configs * 100
        super(Order, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
