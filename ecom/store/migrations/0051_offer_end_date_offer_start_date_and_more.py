# Generated by Django 5.1.3 on 2025-01-20 13:07

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0050_alter_otptoken_otp_code_offer_product_offer'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='offer',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='d2b569', max_length=6),
        ),
    ]
