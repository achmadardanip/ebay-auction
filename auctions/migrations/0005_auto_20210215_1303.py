# Generated by Django 3.1.6 on 2021-02-15 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auto_20210215_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='link',
            field=models.CharField(blank=True, default=None, max_length=500, null=True),
        ),
    ]
