from django import forms
from django.conf import settings
from django.contrib.auth.models import User

# from django.urls import reverse
# from django.forms import ModelForm, DateInput
from tracker.models import Game, League, Profile, Site
from tracker.utils import DistanceError, distance_miles


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"readonly": "readonly"}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "profile_picture",
            "home_address",
            "city",
            "state",
            "zip_code",
        )
        widgets = {
            "home_address": forms.TextInput(
                attrs={
                    "placeholder": "123 Main St",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "placeholder": "City",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "placeholder": "State",
                }
            ),
            "zip_code": forms.TextInput(
                attrs={
                    "placeholder": "12345",
                }
            ),
        }
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "profile_picture": "Profile Picture",
            "home_address": "Home Address",
            "city": "City",
            "state": "State",
            "zip_code": "ZIP Code",
        }


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

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        # If creating a new game, hide mileage field
        # If editing an existing game, show mileage as editable
        if not self.instance.pk:
            # Creating new game - hide mileage field
            self.fields["mileage"].widget = forms.HiddenInput()
            self.fields["mileage"].required = False
        else:
            # Editing existing game - show mileage as editable
            self.fields[
                "mileage"
            ].help_text = "Leave unchanged to recalculate, or enter custom value"

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Only calculate mileage automatically if:
        # 1. Creating a new game (no pk), OR
        # 2. Editing and mileage field wasn't changed by user
        is_new = instance.pk is None
        mileage_changed = "mileage" in self.changed_data
        should_calculate = is_new or not mileage_changed

        if should_calculate and instance.site:
            try:
                destination = instance.site.address

                # Get origin address from user profile or settings default
                origin = settings.DEFAULT_ADDRESS
                if self.user and hasattr(self.user, "profile"):
                    profile_address = self.user.profile.full_address
                    if profile_address:
                        origin = profile_address

                instance.mileage = distance_miles(origin, destination)
            except DistanceError:
                # If API call fails, set mileage to 0
                instance.mileage = 0.0
        elif should_calculate and not instance.site:
            # No site selected, set mileage to 0
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
