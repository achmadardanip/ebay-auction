# Generated by Django 3.1.6 on 2021-02-18 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0015_watchlist_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='closebid',
            name='time',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
