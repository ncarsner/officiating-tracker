from django import forms

from tracker.models import Game, League, Site

# from django.forms import ModelForm, DateInput


class DateInput(forms.DateInput):
    input_type = "date"


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["date", "site", "league", "position"]
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
