# Generated by Django 5.1.3 on 2025-01-05 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0029_alter_otptoken_otp_code_usercoupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='85022b', max_length=6),
        ),
    ]
