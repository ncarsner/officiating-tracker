from django import forms

from tracker.models import Game, League, Site


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["date", "site", "league", "position"]


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["name", "address"]


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ["organization", "assignor", "game_fee", "description"]
