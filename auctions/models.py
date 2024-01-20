from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings 
from django.utils.timezone import now 
from datetime import datetime



class User(AbstractUser):

    def __str__(self):
        return f"{self.id}: Email: {self.email}"
     


    


class Category(models.Model):
    category_name = models.CharField(max_length=256, verbose_name="Category")

    def __str__(self):
        return self.category_name


    
class Listing(models.Model):
    category = models.ManyToManyField(Category, blank=False, related_name="categories")
    listing_title = models.CharField(max_length=256, verbose_name="Title")
    listing_details = models.TextField(verbose_name="Please enter full detailss of your Listing")
    listing_date_time = models.DateTimeField(default = now, verbose_name="Listing time")
    reserve = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Reserve")
    auction_open = models.BooleanField(default = True, verbose_name="Auction Concluded")
    listing_image_url = models.URLField(verbose_name="URL for images for Listing Item")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", verbose_name="Listed by")
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="followed_listings", verbose_name="following",)


    def total_followers(self):
        return self.following.count()

    def get_max_bid(self):
        return self.bids.order_by('-amount').first()
    
    def bid_history(self):
        return self.bids.order_by('-amount')


    def __str__(self):
        max_bid = self.get_max_bid()
        max_bid_amount = max_bid.amount if max_bid else "No bids"
        return f"Listing: {self.listing_title}, Max bid: {max_bid_amount}, listing owned by {self.user }"


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
    

    