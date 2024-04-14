# Generated by Django 5.0.3 on 2024-04-06 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_create_at_order_update_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatuses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.TimeField(auto_now_add=True)),
                ('children', models.PositiveSmallIntegerField(choices=[(1, 'Сформирован'), (2, 'Оплачен'), (3, 'В обработке'), (4, 'Выполнен')], default=1)),
            ],
            options={
                'db_table': 'order_statuses',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_paid', models.BooleanField(default=False)),
                ('price', models.PositiveIntegerField()),
                ('payment_url', models.TextField(blank=True, null=True)),
                ('payment_id', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'payments',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.ManyToManyField(to='orders.orderstatuses'),
        ),
    ]