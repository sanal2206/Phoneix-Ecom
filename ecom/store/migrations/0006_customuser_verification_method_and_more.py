# Generated by Django 5.1.3 on 2024-12-06 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_customuser_is_active_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='verification_method',
            field=models.CharField(choices=[('OTP', 'OTP'), ('Google', 'Google'), ('Facebook', 'Facebook')], default='OTP', max_length=20),
        ),
        migrations.AlterField(
            model_name='otptoken',
            name='otp_code',
            field=models.CharField(default='56c5e4', max_length=6),
        ),
    ]
