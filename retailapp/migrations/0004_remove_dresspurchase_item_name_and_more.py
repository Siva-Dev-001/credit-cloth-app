# Generated by Django 5.2 on 2025-04-27 04:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('retailapp', '0003_purchaseitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dresspurchase',
            name='item_name',
        ),
        migrations.RemoveField(
            model_name='dresspurchase',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='dresspurchase',
            name='unit_price',
        ),
    ]
