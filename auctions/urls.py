from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.new_listing, name="new_listing"), 
    path('listing/<int:listing_id>/', views.listing_details, name='listing_details'),
    path('newbid/<int:listing_id>/', views.newbid, name='newbid'),
    path('follow_tog/<int:listing_id>/', views.follow_tog, name='follow_tog'),
    path('watchlist', views.watchlist, name = "watchlist"), 
    path('comment/<int:listing_id>/', views.comment, name="comment"),
    path('categories', views.categories, name="categories"), 
    path('category_listings/<str:category_name>/', views.category_listings, name="category_listings"),
    
    ]