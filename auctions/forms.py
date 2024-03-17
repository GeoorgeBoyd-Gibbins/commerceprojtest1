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
        widget=forms.NumberInput(attrs={'placeholder': 'Enter your bid in GBP (£)'})
    )


    
    class Meta:
        model = Bid
        fields = ['amount']



class CommentForm(ModelForm):

    class Meta:
        model= Comment
        fields = ['comment_content']
        labels = {'comment_content' : False}
        widgets = {
            'comment_content': forms.Textarea(attrs={
            'placeholder': 'Join the conversation...',
            'class': 'form-control comment-entry-box',
            'rows': 1,
            'style': 'width: 100%; overflow:hidden; resize:none;',
            }),
        }


class CommentReplyForm(ModelForm):

    class Meta:
        model= Comment
        fields = ['comment_content']
        labels = {'comment_content' : False}
        widgets = {
            'comment_content': forms.Textarea(attrs={
            'placeholder': 'Reply to this comment...',
            'class': 'form-control comment-reply-entry-box',
            'rows': 4,
            'style': 'width: 100%; overflow:hidden; resize:none;',
            }),
        }


