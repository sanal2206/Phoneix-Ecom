# Generated by Django 5.1.3 on 2025-01-29 15:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0054_alter_wishlist_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='product',
            field=models.ForeignKey(default=25, on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to='store.product'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='80d948', max_length=6),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='variant',
            field=models.ForeignKey(default=29, on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to='store.variant'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together={('user', 'product', 'variant')},
        ),
    ]
