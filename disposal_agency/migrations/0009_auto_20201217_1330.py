# Generated by Django 3.1 on 2020-12-17 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disposal_agency', '0008_auto_20201216_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disposalentries',
            name='city',
            field=models.CharField(default='indore', max_length=25),
            preserve_default=False,
        ),
    ]
