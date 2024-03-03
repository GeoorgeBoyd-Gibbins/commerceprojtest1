from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import now, timedelta, timezone

from .models import Category, Listing, Comment, Bid, User
from .forms import ListingForm, BidForm, CommentForm




def index(request):
    listings = Listing.objects.filter(auction_open=True).order_by('-closing_time')
    paginator = Paginator(listings, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "auctions/index.html", {
        "page_obj" : page_obj, 
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




def editlisting(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.user != listing.user:
        return render(request, "auctions/forbiddenedit.html", {
            "listing_id" : listing_id,
        })
    
    if request.method == "POST":
        print("New EDIT listing POST received")
        new_category_name = request.POST.get('new_category_name', '').strip().lower()
        if new_category_name:
            # user has specified a new catagory
            existing_categories = Category.objects.values_list('category_name', flat=True)
            existing_categories_lower = [c.lower() for c in existing_categories]
            if new_category_name not in existing_categories_lower:
                # Add new category to database
                Category.objects.create(category_name=new_category_name.title())
                message = "Thanks for your submission, we have added a new category."
                listing.category = new_category_name.title()
                listing.save()
                return HttpResponseRedirect(reverse('editlisting', args=(listing_id,)))
                        

        else:

            # user has submitted a edited listing, assign to variables
            item_category_id = request.POST.get('category')

            if item_category_id is not None:
                try:
                    item_category_id = int(item_category_id)
                    item_category = Category.objects.get(pk=item_category_id)
                except (ValueError, Category.DoesNotExist):
                    # If the category does not exist or the value cannot be converted to an integer
                    item_category = None
                    messages.error(request, "Invalid category selected.")

            item_title = request.POST.get('item_title')

            item_details = request.POST.get('item_details')

            if listing.listing_image_url:

                item_image_url = request.POST.get('item_image_url')

            item_starting_price = request.POST.get('item_starting_price')



            item_reserve = request.POST.get('item_reserve', 1)

        
            item_closing_time = request.POST.get('item_closing_time', '').strip()



            if not item_closing_time:
                item_closing_time = now() + timedelta(days=3)


            if not item_reserve:
                item_reserve = 1

            if not item_starting_price:
                item_starting_price = 1
            

            try:
                item_reserve = Decimal(item_reserve)
                item_starting_price = Decimal(item_starting_price)

            
            except (ValueError, ValidationError):
                messages.error(request, "Invalid numeric value.")
                return redirect('edit_listing', listing_id=listing_id)
                
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
                # update fields from the form
                listing.category = item_category
                listing.listing_title = item_title 
                listing.listing_details = item_details
                listing.reserve = item_reserve
                listing.starting_price = item_starting_price
                listing.closing_time = item_closing_time


                if item_image_url:
                    listing.listing_image_url = item_image_url
                
                # Save the listing
                listing.save()

                messages.success(request, "Your listing has been updated successfully.")

                # Instead of rendering 'auctions/index.html' directly
                return HttpResponseRedirect(reverse('listing_details', args=(listing_id,)))

    else:
        # GET request, populate edit listing form with listing details to edit/;
        categories = Category.objects.all()


        reserve_met = listing.current_bid >= listing.reserve

        bid_made = listing.bid_history().exists()
        
        closing_time = listing.closing_time.strftime('%Y-%m-%dT%H:%M')
        print(closing_time)

        return render(request, "auctions/editlisting.html", {
            "listing" : listing,
            "categories" : categories,
            "reserve_met" : reserve_met,
            "bid_made"  : bid_made,
            "closing_time" : closing_time,
        })


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


            try:
                item_category_id = None if item_category_id == 'none' else int(item_category_id)
                item_category = Category.objects.get(pk=item_category_id)
            
            except:
                item_category = None  # or handle the error as you see fit

            item_title = request.POST.get('item_title')

            item_details = request.POST.get('item_details')

            item_image_url = request.POST.get('item_image_url')

            item_starting_price = request.POST.get('item_starting_price')



            item_reserve = request.POST.get('item_reserve', 1)

        
            item_closing_time = request.POST.get('item_closing_time', '').strip()



            if not item_closing_time:
                item_closing_time = now() + timedelta(days=3)


            if not item_reserve:
                item_reserve = 1

            if not item_starting_price:
                item_starting_price = 1
            

            try:
                item_reserve = Decimal(item_reserve)
                item_starting_price = Decimal(item_starting_price)

            
            except ValidationError as e:
                # Handle validation error if reserve or starting price can't be converted to decimal. 
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
                new_listing.starting_price = item_starting_price
                new_listing.closing_time = item_closing_time


                if item_image_url:
                    new_listing.listing_image_url = item_image_url
                
                # Save the listing
                new_listing.save()

                # Now use the set() method to assign to the ManyToManyField
                new_listing.following.set([new_listing.user])

                listings = Listing.objects.filter(auction_open=True)
                paginator = Paginator(listings, 5)
                page_number = request.GET.get("page")
                page_obj = paginator.get_page(page_number)

                messages.success(request, "Thanks for your Listing, Good Luck!!")

                # Instead of rendering 'auctions/index.html' directly
                return HttpResponseRedirect(reverse('index'))


            
    else:
        categories = Category.objects.all()
        return render(request, "auctions/newlisting.html",{
                    "categories" : categories,
        }
        )


def listing_details(request, listing_id, follow_action=None):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user
    username = user.username.title()
    user_initial = username[0]

    if follow_action and user.is_authenticated:
        if follow_action == 'follow':
            listing.following.add(user)
        elif follow_action == 'unfollow':
            listing.following.remove(user)
        
        return redirect('listing_details', listing_id=listing_id)

    if request.method == "POST":
        new_bid_str = request.POST.get("amount", '0')

        try:
            new_bid = Decimal(new_bid_str)
            if new_bid <= 1:
                # Add an error message to be displayed on the next page
                messages.error(request, "Invalid Bid. Your bid needs to be more than £1.")

            elif new_bid <= listing.current_bid:
                # Add an error message to be displayed on the next page
                messages.error(request, "Invalid Bid. Your bid needs to be more than the current listed price.")

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
                messages.success(request, "Thanks for your bid, Good Luck!!")     
            
            return redirect("listing_details", listing_id=listing_id)
        
        except (InvalidOperation, ValueError, TypeError):
            messages.error(request, "Invalid Bid. You need to enter a number.")
            return redirect("listing_details", listing_id=listing_id)
    else:
        # this request is not POST, initiate forms for Listing Details Page
        form = BidForm()
        comment_form = CommentForm()

        comments = Comment.objects.filter(listing=listing)
        number_comments = comments.count()
        
        # Set user bid default values. 
        reserve_met = False
        user_bid_amount = False
        is_highest_bidder = False
        bid_superceeded = False
        number_user_bids = 0

        # Set bid history values. 
        bid_history = listing.bid_history()
        number_bids = bid_history.count()
        if user.is_authenticated:
            if listing.bid_history().filter(user=user).exists():
                user_bid_amount = listing.bid_history().filter(user=user).first().amount 
                number_user_bids = listing.bid_history().filter(user=user).count()

        # determine if user has bid and if they are the highest bidder.

        highest_bid = listing.get_max_bid()

        

        if number_bids:
            highest_bid_amount = highest_bid.amount
            if listing.get_max_bid().user == user:
                is_highest_bidder = True
            elif user_bid_amount: 
               bid_superceeded = True

        # Determine if reserve met.
        reserve = listing.reserve
        if listing.current_bid >= reserve:
            reserve_met = True

        # Determine if user is following item 
        following = request.user in listing.following.all()

        # get followers and countr them 
        followers = listing.following.all()
        following_count = followers.count() 


        # Calculate time left 
        time_left_delta = listing.closing_time - now()
        days = time_left_delta.days
        hours, remainder = divmod(time_left_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60) 
        time_left_str = f"{days} days {hours}h {minutes}m"
        if time_left_delta.total_seconds() <= 0:
            time_left_str = "Auction concluded."
        

        


        if number_bids:
            # Bids have been made so for current price render highest bid. 
            return render(request, 'auctions/listing_details.html', {
                        'listing': listing,
                        'form' : form,
                        'listing_num' : listing_id,
                        'username' : username,
                        'user_initial' : user_initial, 
                        'bid_history' : bid_history, 
                        'following' : following,
                        'followers' : followers, 
                        'following_count' : following_count, 
                        'comment_form' : comment_form, 
                        'comments' : comments,
                        'number_comments' : number_comments, 
                        'time_left' : time_left_str,
                        'number_bids' : number_bids,
                        'highest_bid' : highest_bid_amount,
                        'reserve' : reserve,
                        'reserve_met' : reserve_met, 
                        'user_bid_amount' : user_bid_amount,
                        'number_user_bids' : number_user_bids, 
                        'is_highest_bidder' : is_highest_bidder,
                        'bid_superceeded' : bid_superceeded, 
            }) 
        
        else:
            #No bids have been made, render starting price as current price
            starting_price = listing.starting_price
            
            return render(request, 'auctions/listing_details.html', {
                        'listing': listing,
                        'form' : form,
                        'listing_num' : listing_id,
                        'username' : username,
                        'user_initial' : user_initial, 
                        'bid_history' : bid_history, 
                        'following' : following,
                        'followers' : followers, 
                        'following_count' : following_count, 
                        'comment_form' : comment_form, 
                        'comments' : comments,
                        'number_comments' : number_comments, 
                        'time_left' : time_left_str,
                        'number_bids' : number_bids,
                        'highest_bid' : starting_price,
                        'reserve' : reserve,
                        'reserve_met' : reserve_met, 
                        'user_bid_amount' : user_bid_amount,
                        'number_user_bids' : number_user_bids, 
                        'is_highest_bidder' : is_highest_bidder,
                        'bid_superceeded' : bid_superceeded, 
}) 



def watchlist(request):
    user = request.user
    if user.is_authenticated:
        followed_listings = Listing.objects.filter(following=request.user)
        return render(request, 'auctions/followed_listings.html', 
                      {'followed_listings': followed_listings, 
                       })
    
    else:
        # Handle the case where the user is not logged in
        listings = Listing.objects.filter(auction_open=True)
        paginator = Paginator(listings, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(request, 'auctions/index.html', 
                      {'message': 'You need to be logged in to view the Watchlist page.',
                       "page_obj" : page_obj, 
                       })

    

def comment(request, listing_id):
    comment_content = " "

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_content = comment_form.cleaned_data['comment_content']
    
    # Create a new comment object
    new_comment = Comment()

    # populate comment object fields
    new_comment.user = request.user

    new_comment.comment_content = comment_content

    new_comment.listing = get_object_or_404(Listing, pk=listing_id)

    # Save the new comment
    new_comment.save()


    listings = Listing.objects.filter(auction_open=True)
    paginator = Paginator(listings, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    messages.success(request, "Thanks for your comment.")
    return redirect("listing_details", listing_id=listing_id) 

def categories(request):
    available_categories = Category.objects.all()
    print(available_categories)
    return render(request, "auctions/categories.html", {
        "categories" : available_categories, 
    } )

def category_listings(request, category_name):

    # Get the category object, or return a 404 if not found
    category = get_object_or_404(Category, category_name=category_name)



    relevent_listings = Listing.objects.filter(category=category)

    paginator = Paginator(relevent_listings, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "auctions/categorylistings.html", {
        "listings" : relevent_listings, 
        "category_name" : category_name, 
        "page_obj" : page_obj, 
    })



def commentguidelines(request, listing_id):
    return render(request,"auctions/commentguidelines.html",{
        "listing_id" : listing_id,
    })


    