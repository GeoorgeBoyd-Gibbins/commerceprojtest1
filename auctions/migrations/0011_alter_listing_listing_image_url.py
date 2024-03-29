# Generated by Django 5.0.1 on 2024-02-05 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_alter_listing_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='listing_image_url',
            field=models.URLField(max_length=500, verbose_name='URL for images for Listing Item'),
        ),
    ]
