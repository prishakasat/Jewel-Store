# Generated by Django 5.0.5 on 2024-05-15 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_feedback_product_id_feedback_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='address',
            field=models.CharField(max_length=255, verbose_name='Shipping Address'),
        ),
    ]
