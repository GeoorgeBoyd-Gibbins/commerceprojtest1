# Generated by Django 5.0.1 on 2024-01-19 02:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='max_bid',
        ),
    ]
