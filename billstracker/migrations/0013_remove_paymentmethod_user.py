# Generated by Django 5.1.5 on 2025-01-16 12:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billstracker', '0012_paymentmethod_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentmethod',
            name='user',
        ),
    ]
