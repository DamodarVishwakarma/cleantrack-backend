# Generated by Django 3.1 on 2020-12-16 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transporter', '0011_auto_20201216_1901'),
        ('disposal_agency', '0007_auto_20201216_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='disposalrevision',
            name='disposal_entry',
        ),
        migrations.AddField(
            model_name='disposalrevision',
            name='consignment',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='transporter.consignment'),
            preserve_default=False,
        ),
    ]