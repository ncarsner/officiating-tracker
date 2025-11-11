from django import forms
from django.contrib.auth.models import User
from django.urls import reverse

from tracker.models import Game, League, Profile, Site


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
        super().__init__(*args, **kwargs)

        base = (
            "w-full rounded-xl border border-zinc-300 dark:border-zinc-700 "
            "bg-white dark:bg-zinc-800 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        )
        cb = "h-4 w-4 rounded border-zinc-300 text-indigo-600 focus:ring-indigo-500"

        self.fields["date"].widget.attrs.update({"class": base})
        self.fields["site"].widget.attrs.update(
            {
                "class": base,
                "hx-trigger": "change",
                "hx-target": "#id_mileage",
                "hx-swap": "outerHTML",
                "hx-indicator": ".htmx-indicator",
                **({"hx-get": reverse("site_distance")} if request else {}),
            }
        )
        print(self.fields["site"].widget.attrs)
        self.fields["league"].widget.attrs.update({"class": base})
        self.fields["position"].widget.attrs.update({"class": base})
        self.fields["mileage"].widget.attrs.update({"class": base})
        self.fields["fee_paid"].widget.attrs.update({"class": cb})
        self.fields["mileage_paid"].widget.attrs.update({"class": cb})


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["name", "address"]


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = ["organization", "assignor", "game_fee", "description"]
