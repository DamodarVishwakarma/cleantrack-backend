# Generated by Django 3.1 on 2020-12-16 06:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporter', '0009_auto_20201215_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionentries',
            name='vehicle_number',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{1,4}$', message='Invalid Vehicle number')]),
        ),
    ]
