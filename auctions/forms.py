from django.forms import ModelForm
from django import forms
from .models import User, Category, Listing, Comment, Bid 

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'listing_title', 'listing_details', 'reserve', 'listing_image_url'  ]
        widgets = {
            'listing_details': forms.Textarea(attrs={'rows': 4, 'cols': 40})
        }


class BidForm(ModelForm):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text='Enter your bid in GBP (£)',
        widget=forms.NumberInput(attrs={'placeholder': 'Enter your bid in GBP (£)'})
    )


    
    class Meta:
        model = Bid
        fields = ['amount']