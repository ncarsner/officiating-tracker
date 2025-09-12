from django import forms
from django.contrib.auth.models import User

from tracker.models import Game, League, Profile, Site

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


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["name", "address"]


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ["organization", "assignor", "game_fee", "description"]
