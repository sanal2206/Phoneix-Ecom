# Generated by Django 5.1.3 on 2024-12-10 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_colour_storage_rename_brand_product_brand_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='7a6c7b', max_length=6),
        ),
        migrations.AlterField(
            model_name='variant',
            name='colour',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='store.colour'),
        ),
        migrations.AlterField(
            model_name='variant',
            name='storage',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='store.storage'),
        ),
    ]
