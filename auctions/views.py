from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now, timedelta

from .models import Category, Listing, Comment, Bid, User
from .forms import ListingForm, BidForm 




def index(request):
    listings = Listing.objects.filter(auction_open=True)

    return render(request, "auctions/index.html", {
        "listings" : listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def new_listing(request):
    if request.method == "POST":
        print("New listing POST received")
        print(request)
        new_category_name = request.POST.get('new_category_name')
        if new_category_name:
            # user has specified a new catagory
            new_category_name = new_category_name.strip().lower()
            existing_categories = Category.objects.values_list('category_name', flat=True)
            existing_categories_lower = [c.lower() for c in existing_categories]
            if new_category_name not in existing_categories_lower:
                # Add new category to database
                Category.objects.create(category_name=new_category_name.title())
                # Redirect or update as necessary
                categories_updated = Category.objects.all()
                message = "Thanks for your submission, we have added a new category."
                return render(request, "auctions/newlisting.html",{
                    "categories" : categories_updated, 
                    "message" : message, 
                    }) 
            
            else:

                categories = Category.objects.all()
                message = f"Thanks but we already have a {new_category_name} Category"
                return render(request, "auctions/newlisting.html",{
                    "categories" : categories, 
                    "message" : message, 
                })
    
        else:

            # user has submitted a new listing, assign to variables
            item_category_id = request.POST.get('category')

            if item_category_id == 'none':
                item_category_id = None 

            item_category_id = int(item_category_id)

            try:
                item_category = Category.objects.get(pk=item_category_id)
            
            except Category.DoesNotExist:
                item_category = None  # or handle the error as you see fit

            item_title = request.POST.get('item_title')

            item_details = request.POST.get('item_details')

            item_image_url = request.POST.get('item_image_url')

            item_starting_price = request.POST.get('item_starting_price', 1)



            item_reserve = request.POST.get('item_reserve', 1)

        
            item_closing_time = request.POST.get('item_closing_time', '').strip()



            if not item_closing_time:
                item_closing_time = now() + timedelta(days=7)


            if not item_reserve:
                item_reserve = 1

            if not item_starting_price:
                item_starting_price = 1
            

            try:
                item_reserve = Decimal(item_reserve)
            
            except ValidationError as e:
                # Handle validation error if reserve can't be converted to decimal. 
                return render(request, "auctions/newlisting.html", {
                    "message": e.messages,
                    "categories": Category.objects.all()
                })
            
            details_len = len(item_details)
            title_len = len(item_title)

            if title_len == 0:
                # Handle validation error if title  blank. 
                return render(request, "auctions/newlisting.html", {
                    "message": "Details for title can't be blank",
                    "categories": Category.objects.all(),
                })
            
            elif details_len == 0:
                # Handle validation error if title blank. 
                return render(request, "auctions/newlisting.html", {
                    "message": "Details for listing can't be blank", 
                    "categories": Category.objects.all(),
                })
            
            elif title_len > 256:
                # Handle validation error if title exceeds length limit
                return render(request, "auctions/newlisting.html", {
                    "message": "Title can't exceed 256 characters", 
                    "categories": Category.objects.all(), 
                })
                
            else:
                # POST listing is valid, create new Listing 
                new_listing = Listing()

                # Set the user to the currently logged-in user
                new_listing.user = request.user

                # Set other fields from the form
                new_listing.category = item_category
                new_listing.listing_title = item_title 
                new_listing.listing_details = item_details
                new_listing.reserve = item_reserve
                new_listing.starting_bid = item_starting_price
                new_listing.closing_time = item_closing_time


                if item_image_url:
                    new_listing.listing_image_url = item_image_url
                
                # Save the listing
                new_listing.save()

                # Now use the set() method to assign to the ManyToManyField
                new_listing.following.set([new_listing.user])


                # Redirect to a new URL, display a success message, etc.
                return render(request, "auctions/index.html", {
                    "message" : "Thanks for your Listing, Good Luck!!",  
                })




    else:
        categories = Category.objects.all()
        return render(request, "auctions/newlisting.html",{
                    "categories" : categories,
        }
        )


def listing_details(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bid_history = listing.bid_history()
    form = BidForm()
    following = request.user in listing.following.all()
    return render(request, 'auctions/listing_details.html', {
                  'listing': listing,
                  'form' : form,
                  'listing_num' : listing_id,
                  'bid_history' : bid_history, 
                  'following' : following, 
     }) 



def newbid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    listing_price = listing.current_bid
    new_bid = Decimal(request.POST["amount"])
    if new_bid <= listing_price:
        return render(request, "auctions/index.html", {
            
            'message2' : "Invalid Bid. Your bid needs to be more that the current listed price."
        })
    
    else:
        #Create a new bid
        new_bid_instance = Bid ()

        # Set the user to the currently logged-in user
        new_bid_instance.user = request.user

        # Set the listing the bid relates to. 
        new_bid_instance.listing= listing

        # Set the amount 

        new_bid_instance.amount = new_bid

        # Save the listing
        new_bid_instance.save()


        return render(request, "auctions/index.html", {
            
            'message3' : "Thanks for your bid, good luck!."
        }) 



@login_required
def follow_tog(request, listing_id):#
    listing = get_object_or_404(Listing, pk=listing_id)
    bid_history = listing.bid_history()
    form = BidForm()
    following = request.user in listing.following.all()
    if following:
        listing.following.remove(request.user)
        return render(request, 'auctions/listing_details.html', {
                  'listing': listing,
                  'form' : form,
                  'listing_num' : listing_id,
                  'bid_history' : bid_history, 
                  'following' : False,
        }
        )
    
    else:
        listing.following.add(request.user)
        return render(request, 'auctions/listing_details.html', {
            'listing': listing,
            'form' : form,
            'listing_num' : listing_id,
            'bid_history' : bid_history, 
            'following' : True,
        }
        )



def watchlist(request):
    user = request.user
    if user.is_authenticated:
        followed_listings = Listing.objects.filter(following=request.user)
        return render(request, 'auctions/followed_listings.html', 
                      {'followed_listings': followed_listings, 
                       })
    
    else:
        # Handle the case where the user is not logged in
        return render(request, 'auctions/index.html', 
                      {'message': 'You need to be logged in to view the Watchlist page.'})

    