# Generated by Django 4.0.2 on 2022-04-15 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_wishlist_id_pr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Product Image'),
        ),
    ]