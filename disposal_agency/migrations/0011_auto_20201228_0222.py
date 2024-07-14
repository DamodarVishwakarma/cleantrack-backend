# Generated by Django 3.1 on 2020-12-28 02:22

import digitalplatformbackend.custom_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disposal_agency', '0010_auto_20201222_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disposalentries',
            name='loaded_vehicle_img',
            field=digitalplatformbackend.custom_fields.CustomImageField(upload_to='Images/Disposals'),
        ),
        migrations.AlterField(
            model_name='disposalentries',
            name='vehicle_number_img',
            field=digitalplatformbackend.custom_fields.CustomImageField(upload_to='Images/Disposals'),
        ),
        migrations.AlterField(
            model_name='disposalentries',
            name='weighment_slip_img',
            field=digitalplatformbackend.custom_fields.CustomImageField(upload_to='Images/Disposals'),
        ),
        migrations.AlterField(
            model_name='disposalrevision',
            name='disposal_vehicle_number_img',
            field=digitalplatformbackend.custom_fields.CustomImageField(upload_to='Images/Revisions'),
        ),
    ]