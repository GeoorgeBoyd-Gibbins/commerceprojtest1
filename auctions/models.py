from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings 
from django.utils.timezone import now
from datetime import datetime, timedelta

# used to calculate listing closing time
def thirtysixhours():
    return now() + timedelta(hours=36)


class User(AbstractUser):

    def __str__(self):
        return f"{self.id}: Email: {self.email}"
     

class Category(models.Model):
    category_name = models.CharField(max_length=256, verbose_name="Category")

    def __str__(self):
        return self.category_name


    
class Listing(models.Model):

    # define model
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null = True, blank=True, related_name="listings")
    listing_title = models.CharField(max_length=256, verbose_name="Title")
    listing_details = models.TextField(verbose_name="Please enter full detailss of your Listing")
    listing_date_time = models.DateTimeField(default = now, verbose_name="Listing time")
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default = 1, verbose_name="Current Bid")
    reserve = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Reserve")
    closing_time = models.DateTimeField(default = thirtysixhours, verbose_name="closingtime")
    auction_open = models.BooleanField(default = True, verbose_name="Auction Open")
    listing_image_url = models.URLField(verbose_name="URL for images for Listing Item")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", verbose_name="Listed by")
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="followed_listings", verbose_name="following")

    #define other methods 
    def total_followers(self):
        return self.following.count()

    def get_max_bid(self):
        return self.bids.order_by('-amount').first()
    
    def bid_history(self):
        return self.bids.order_by('-amount')

    def __str__(self):
        return f"Listing ID: {self.id}. Listing: {self.listing_title}.  Listed by: {self.user }. Auction open: {self.auction_open}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments", verbose_name="Comentor")
    comment_content = models.CharField(max_length=5000, verbose_name="Comment")
    comment_time = models.DateTimeField(default= now, verbose_name="Comment Made at")
    
    def __str__(self):
        return f"Comment by {self.user} on {self.listing} at {self.comment_time}. Comment: {self.comment_content}"
    




class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids', verbose_name="Bidder")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids', verbose_name="Listing")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bid Amount")
    time = models.DateTimeField(default=now, verbose_name="Bid Time")

    class Meta:
        # This ensures that the latest bids are always first
        ordering = ['-time']

    def __str__(self):
        return f"{self.user} bid on {self.listing} for {self.amount}"
    

    