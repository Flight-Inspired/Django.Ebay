from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from decimal import Decimal

from .forms import ListingForm, BidForm
from .models import AuctionListing, User, Watchlist, Bid, Comment


def index(request):
    active_listings = AuctionListing.objects.filter(is_active=True)
    for listing in active_listings:
        # Fetch the current bid for each listing and attach it to the instance
        listing.current_bid = Bid.objects.filter(listing=listing).aggregate(Max('amount'))['amount__max']
    return render(request, "auctions/index.html", {'listings': active_listings})


@login_required
def add_comment(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(AuctionListing, pk=listing_id)
        commenter = request.user
        comment_text = request.POST.get('comment_text')
        new_comment = Comment(listing=listing, commenter=commenter, comment_text=comment_text)
        new_comment.save()
        return redirect('listing_detail', pk=listing_id)
    else:
        pass


@login_required
def add_to_watchlist(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    user = request.user
    is_in_watchlist = Watchlist.objects.filter(user=user, listing=listing).exists()

    print(f"Is listing in watchlist: {is_in_watchlist}")

    if is_in_watchlist:
        print("Removing from watchlist")
        Watchlist.objects.filter(user=user, listing=listing).delete()
        print("Removed from watchlist successfully")
    else:
        print("Adding to watchlist")
        Watchlist.objects.create(user=user, listing=listing)
        print("Added to watchlist successfully")

    return redirect('listing_detail', pk=listing_id)



def all_listings(request, category_name=None):
    if category_name:
        active_listings = AuctionListing.objects.filter(category=category_name, is_active=True)
        inactive_listings = AuctionListing.objects.filter(category=category_name, is_active=False)
    else:
        active_listings = AuctionListing.objects.filter(is_active=True)
        inactive_listings = AuctionListing.objects.filter(is_active=False)

    for listing in active_listings:
        listing.current_bid = Bid.objects.filter(listing=listing).aggregate(Max('amount'))['amount__max']

    for listing in inactive_listings:
        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
        if highest_bid:
            listing.winning_bidder = highest_bid.bidder
            listing.winning_amount = highest_bid.amount

    return render(request, 'all_listings.html', {
        'active_listings': active_listings,
        'inactive_listings': inactive_listings,
    })





def category_list(request):
    # Fetch all categories
    categories = AuctionListing.objects.values_list('category', flat=True).distinct()
    return render(request, 'category_list.html', {'categories': categories})

def listings_by_category(request, category_name):
    if category_name:
        active_listings = AuctionListing.objects.filter(category=category_name, is_active=True)
        inactive_listings = AuctionListing.objects.filter(category=category_name, is_active=False)
    else:
        active_listings = AuctionListing.objects.filter(is_active=True)
        inactive_listings = AuctionListing.objects.filter(is_active=False)

    for listing in active_listings:
        listing.current_bid = Bid.objects.filter(listing=listing).aggregate(Max('amount'))['amount__max']

    for listing in inactive_listings:
        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
        if highest_bid:
            listing.winning_bidder = highest_bid.bidder
            listing.winning_amount = highest_bid.amount

    return render(request, 'all_listings.html', {
        'active_listings': active_listings,
        'inactive_listings': inactive_listings,
    })


@login_required
def close_auction(request, pk):
    listing = get_object_or_404(AuctionListing, pk=pk)

    if request.method == 'POST' and request.user == listing.created_by:
        if listing.is_active:
            # Mark the listing as inactive
            listing.is_active = False
            listing.save()

            # Retrieve the highest bid for this listing
            highest_bid = listing.current_bid

            # Identify the winning bidder based on the highest bid
            winning_bidder = highest_bid.bidder if highest_bid else None

            # Print the winning bidder's username and the winning amount
            if winning_bidder:
                print(f"The winning bidder for listing {listing.id} is: {winning_bidder.username}")
                if highest_bid:
                    print(f"The winning amount: ${highest_bid}")
                else:
                    print("No winning amount found")
            else:
                print(f"No winning bidder for listing {listing.id}")

    return redirect('listing_detail', pk=listing.pk)



@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            # Extract cleaned data
            cleaned_data = form.cleaned_data
            # Get the currently logged-in user
            created_by = request.user

            try:
                # Create a new listing
                new_listing = AuctionListing.objects.create(
                    title=cleaned_data['title'],
                    description=cleaned_data['description'],
                    starting_bid=cleaned_data['starting_bid'],
                    image_url=cleaned_data['image_url'],
                    category=cleaned_data['category'],
                    created_by=created_by
                )
                # Redirect to the newly created listing page
                return redirect('listing_detail', pk=new_listing.pk)
            except Exception as e:
                # Handle exceptions if any during listing creation
                messages.error(request, f"Failed to create the listing: {str(e)}")
        else:
            # If the form is not valid, display error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = ListingForm()

    return render(request, 'create_listing.html', {'form': form})



def listing_detail(request, pk):
    listing = get_object_or_404(AuctionListing, pk=pk)
    in_watchlist = False

    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()

    current_bid = Bid.objects.filter(listing=listing).aggregate(Max('amount'))['amount__max']
    starting_bid = listing.starting_bid
    comments = Comment.objects.filter(listing_id=listing.id)

    if current_bid is not None:
        current_bid = Decimal(str(current_bid))
        min_bid = current_bid + Decimal('0.01')
    else:
        min_bid = starting_bid

    winning_bidder = None
    winning_amount = None

    if not listing.is_active:
        highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
        if highest_bid:
            winning_bidder = highest_bid.bidder
            winning_amount = highest_bid.amount

    if request.method == 'POST' and request.user.is_authenticated:
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['bid_amount']
            new_bid = Bid(listing=listing, bidder=request.user, amount=bid_amount)
            new_bid.save()
            return HttpResponseRedirect(reverse('listing_detail', args=[pk]))
    else:
        form = BidForm()

    context = {
        'listing': listing,
        'in_watchlist': in_watchlist,
        'current_bid': current_bid,
        'min_bid': min_bid,
        'winning_bidder': winning_bidder,
        'winning_amount': winning_amount,
        'comments': comments,
        'form': form,
    }

    return render(request, 'listing_detail.html', context)


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
def watchlist_view(request):
    user = request.user
    watchlist_items = Watchlist.objects.filter(user=user).select_related('listing')

    for item in watchlist_items:
        item.listing.current_bid = Bid.objects.filter(listing=item.listing).aggregate(Max('amount'))['amount__max']

    for item in watchlist_items:
        highest_bid = Bid.objects.filter(listing=item.listing).order_by('-amount').first()
        if highest_bid:
            item.listing.winning_bidder = highest_bid.bidder
            item.listing.winning_amount = highest_bid.amount

    active_watchlist_items = [item for item in watchlist_items if item.listing.is_active]
    inactive_watchlist_items = [item for item in watchlist_items if not item.listing.is_active]

    winning_bidder = request.user if inactive_watchlist_items and inactive_watchlist_items[0].listing.winning_bidder == request.user else None

    return render(request, 'watchlist.html', {
        'active_watchlist_items': active_watchlist_items,
        'inactive_watchlist_items': inactive_watchlist_items,
        'winning_bidder': winning_bidder,
    })
