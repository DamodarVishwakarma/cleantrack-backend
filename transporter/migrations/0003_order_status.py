# Generated by Django 3.1 on 2020-11-18 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transporter', '0002_auto_20201106_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(1, 'Ongoing'), (2, 'Completed')], default=1),
        ),
    ]
