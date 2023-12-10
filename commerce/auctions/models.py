# models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models

class User(AbstractUser):
    watchlist = models.ManyToManyField('AuctionListing', related_name='user_watchlist', blank=True)


class AuctionListing(models.Model):
    # ForeignKeys
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_listings')
    created_at = models.DateTimeField(auto_now_add=True)
    # Fields
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image_url = models.URLField(blank=True)

    # Category fields
    CATEGORY_CHOICES = [
        ('uncategorized', 'Uncategorized'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('furniture', 'Furniture'),
        ('vehicles', 'Vehicles'),
        ('books', 'Books'),
        # Add more categories as needed
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='uncategorized')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Bid(models.Model):
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.amount} on {self.listing.title} by {self.bidder.username}"


class Comment(models.Model):
    # ForeignKeys
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_made')
    # Fields
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter.username} - {self.created_at}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_watchlist')
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='list_watchlist')

