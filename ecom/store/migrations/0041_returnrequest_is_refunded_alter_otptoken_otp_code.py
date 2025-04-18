# Generated by Django 5.1.3 on 2025-01-14 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0040_returnrequest_user_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='returnrequest',
            name='is_refunded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='0321c6', max_length=6),
        ),
    ]
