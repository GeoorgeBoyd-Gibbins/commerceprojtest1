from django.forms import ModelForm
from .models import User, Category, Listing, Comment, Bid 

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'listing_title', 'listing_details', 'reserve', 'listing_image_url'  ]
