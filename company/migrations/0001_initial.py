from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=225)),
                ('street', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=255, null=True)),
                ('company_type', models.IntegerField(blank=True, choices=[(1, 'Collection Agency'), (2, 'Disposal Agency'), (4, 'Others')], null=True)),
                ('company_status', models.IntegerField(choices=[(1, 'Active'), (2, 'Deactive')], default=2)),
            ],
            options={
                'verbose_name_plural': 'Companies',
            },
        ),
    ]
