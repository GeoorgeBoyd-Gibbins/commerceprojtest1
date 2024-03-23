from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newlisting", views.new_listing, name="new_listing"), 
    path('listing/<int:listing_id>/', views.listing_details, name='listing_details'),
    path('listing/<int:listing_id>/<str:follow_action>/', views.listing_details, name='listing_details_with_follow_action'),
    path('watchlist', views.watchlist, name = "watchlist"), 
    path('comment/<int:listing_id>/', views.comment, name="comment"),
    path('comment/reply/<int:listing_id>/<int:parent_id>/', views.comment_reply, name="comment_reply"),
    path('categories', views.categories, name="categories"), 
    path('category_listings/<str:category_name>/', views.category_listings, name="category_listings"),
    path('commentguidelines/<int:listing_id>/', views.commentguidelines, name="commentguidelines"),
    path('editlisting/<int:listing_id>/', views.editlisting, name="editlisting" ),
    path('listing/<int:listing_id>/<int:comment_id>/<str:comment_like_action>/', views.listing_details, name='listing_details_with_comment_like_action'),
    
    ]
