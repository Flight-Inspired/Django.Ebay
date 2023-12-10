from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # Your existing URL patterns
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing/', views.create_listing, name='create_listing'),
    path('listing_detail/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('add_to_watchlist/<int:listing_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('close_auction/<int:pk>/', views.close_auction, name='close_auction'),
    path('all_listings/', views.all_listings, name='all_listings'),
    path('all_listings/<str:category_name>/', views.all_listings, name='all_listings_category'),
    path('add_comment/<int:listing_id>/', views.add_comment, name='add_comment'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<str:category_name>/', views.listings_by_category, name='listings_by_category'),



]
