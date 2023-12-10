# Generated by Django 4.2.7 on 2023-12-08 03:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0005_remove_auctionlisting_image_auctionlisting_image_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auctionlisting",
            name="category",
            field=models.CharField(
                choices=[
                    ("uncategorized", "Uncategorized"),
                    ("electronics", "Electronics"),
                    ("clothing", "Clothing"),
                    ("furniture", "Furniture"),
                    ("vehicles", "Vehicles"),
                    ("books", "Books"),
                ],
                default="uncategorized",
                max_length=50,
            ),
        ),
    ]