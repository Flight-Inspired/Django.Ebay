# Generated by Django 4.2.7 on 2023-12-08 07:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0009_user_watchlist_alter_watchlist_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="watchlist",
            name="listing",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="list_watchlist",
                to="auctions.auctionlisting",
            ),
        ),
    ]
