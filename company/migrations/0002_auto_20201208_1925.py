# Generated by Django 3.1 on 2020-12-08 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='id',
            field=models.IntegerField(default=None, primary_key=True, serialize=False),
        ),
    ]
