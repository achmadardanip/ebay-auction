from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=64)
    link = models.CharField(max_length=500, default=None, blank=True, null=True)

class Listing(models.Model):
    owner = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    category = models.CharField(max_length=64, null=True)
    link = models.CharField(max_length=500, default=None, blank=True, null=True)
    condition = models.CharField(max_length=64, default=None, blank=True, null=True)
    time = models.CharField(max_length=64)
        
class Bid(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    listingId = models.IntegerField()
    bid = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    time = models.CharField(max_length=64, null=True)

class Comment(models.Model):
    user = models.CharField(max_length=64)
    time = models.CharField(max_length=64)
    comment = models.TextField()
    listingId = models.IntegerField()

class Watchlist(models.Model):
    user = models.CharField(max_length=64)
    listingId = models.IntegerField()
    time = models.CharField(max_length=64, null=True)

class Closebid(models.Model):
    owner = models.CharField(max_length=64)
    winner = models.CharField(max_length=64)
    listingId = models.IntegerField()
    winprice = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    time = models.CharField(max_length=64, null=True)

class allListing(models.Model):
    listingId = models.IntegerField()
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(max_length=64, null=True)
    link = models.CharField(max_length=64, default=None, blank=True, null=True)
    time = models.CharField(max_length=64, null=True)