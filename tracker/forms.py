from django import forms
from tracker.models import Game, Site, League

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['date', 'site', 'league', 'position', 'fee_paid', 'is_volunteer', 'mileage', 'mileage_paid']

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['name', 'address']

class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ['organization', 'assignor', 'game_fee', 'description']