# Generated by Django 5.2 on 2025-04-27 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailapp', '0007_dresspurchase_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dresspurchase',
            name='purchase_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
