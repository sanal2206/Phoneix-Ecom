# Generated by Django 5.1.3 on 2024-12-04 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_rename_tp_created_at_otptoken_otp_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='43304f', max_length=6),
        ),
    ]
