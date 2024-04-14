# Generated by Django 5.0.3 on 2024-04-07 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_remove_order_status_delete_orderstatuses_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('created', 'Сформирован'), ('payed', 'Оплачен'), ('working', 'В обработке'), ('done', 'Выполнен')], default='created', max_length=40),
        ),
    ]