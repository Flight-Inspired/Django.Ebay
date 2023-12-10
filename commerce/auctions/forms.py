from django import forms

class ListingForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.DecimalField(decimal_places=2, max_digits=10)
    image_url = forms.URLField(required=False)

    CATEGORY_CHOICES = [
        ('uncategorized', 'Uncategorized'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('furniture', 'Furniture'),
        ('vehicles', 'Vehicles'),
        ('books', 'Books'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)


class BidForm(forms.Form):
    bid_amount = forms.DecimalField(min_value=0.01)
