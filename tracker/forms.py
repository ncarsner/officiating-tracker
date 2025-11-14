from django import forms
from django.contrib.auth.models import User
from django.urls import reverse

from tracker.models import Game, League, Profile, Site
from tracker.utils import distance_miles, DistanceError

# from django.forms import ModelForm, DateInput


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("user", "location")


class DateInput(forms.DateInput):
    input_type = "date"


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            "date",
            "site",
            "league",
            "fee_paid",
            "mileage_paid",
            "mileage",
            "position",
        ]
        widgets = {
            "date": DateInput(),
        }

    def __init__(self, *args, request=None, **kwargs):
        # Remove user parameter - not needed for now
        kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Make mileage field read-only in the form
        self.fields['mileage'].widget.attrs['readonly'] = True
        self.fields['mileage'].help_text = 'Calculated automatically from default location'

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Use default Nashville address for testing
        DEFAULT_ORIGIN = "1409 12th Ave S, Nashville, TN 37203"
        
        # Calculate mileage if a site is selected
        if instance.site:
            try:
                destination = instance.site.address
                instance.mileage = distance_miles(DEFAULT_ORIGIN, destination)
            except DistanceError:
                # If API call fails, keep the existing mileage or set to 0
                if not instance.mileage:
                    instance.mileage = 0.0
        
        if commit:
            instance.save()
        return instance


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["name", "address"]


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ["organization", "assignor", "game_fee", "description"]
