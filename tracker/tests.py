from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from tracker.forms import GameForm, LeagueForm, SiteForm
from tracker.mileage import mileage_by, total_mileage
from tracker.models import Game, League, Location, Profile, Site
from tracker.utils import DistanceError, distance_miles, resolve_origin


class ProfileModelTest(TestCase):
    """Tests for the Profile model."""

    def test_profile_created_on_user_creation(self):
        """Test that a profile is automatically created when a user is created."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)

    def test_profile_str_with_full_name(self):
        """Test profile string representation with first and last name."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        user.profile.first_name = "John"
        user.profile.last_name = "Doe"
        user.profile.save()
        self.assertEqual(str(user.profile), "John Doe")

    def test_profile_str_without_name(self):
        """Test profile string representation without name defaults to username."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertEqual(str(user.profile), "testuser")

    def test_profile_full_address_property(self):
        """Test full_address property combines address fields."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        user.profile.home_address = "123 Main St"
        user.profile.city = "Nashville"
        user.profile.state = "TN"
        user.profile.zip_code = "37203"
        user.profile.save()
        expected = "123 Main St, Nashville, TN, 37203"
        self.assertEqual(user.profile.full_address, expected)

    def test_profile_full_address_with_partial_data(self):
        """Test full_address property with partial address data."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        user.profile.home_address = "123 Main St"
        user.profile.city = "Nashville"
        user.profile.save()
        expected = "123 Main St, Nashville"
        self.assertEqual(user.profile.full_address, expected)

    def test_profile_full_address_falls_back_to_location(self):
        """Test full_address property falls back to location field."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        user.profile.location = "Old Location Format"
        user.profile.save()
        self.assertEqual(user.profile.full_address, "Old Location Format")

    def test_profile_display_name_with_full_name(self):
        """Test display_name property with first and last name."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        user.profile.first_name = "Jane"
        user.profile.last_name = "Smith"
        user.profile.save()
        self.assertEqual(user.profile.display_name, "Jane Smith")

    def test_profile_display_name_with_first_name_only(self):
        """Test display_name property with only first name."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        user.profile.first_name = "Jane"
        user.profile.save()
        self.assertEqual(user.profile.display_name, "Jane")

    def test_profile_display_name_without_name(self):
        """Test display_name property without name defaults to username."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertEqual(user.profile.display_name, "testuser")

    def test_profile_location_can_be_set(self):
        """Test that profile location can be updated."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        user.profile.location = "123 Main St, Nashville, TN"
        user.profile.save()
        self.assertEqual(user.profile.location, "123 Main St, Nashville, TN")


class LocationModelTest(TestCase):
    """Tests for the Location model."""

    def test_location_creation(self):
        """Test creating a location."""
        location = Location.objects.create(
            name="Test Stadium",
            latitude=36.1627,
            longitude=-86.7816,
            address="123 Stadium Dr, Nashville, TN 37203",
        )
        self.assertEqual(str(location), "Test Stadium")
        self.assertEqual(location.latitude, 36.1627)


class SiteModelTest(TestCase):
    """Tests for the Site model."""

    def test_site_creation(self):
        """Test creating a site."""
        site = Site.objects.create(
            name="Community Center", address="456 Oak St, Nashville, TN 37203"
        )
        self.assertEqual(str(site), "Community Center")
        self.assertEqual(site.address, "456 Oak St, Nashville, TN 37203")

    def test_site_name_unique(self):
        """Test that site names must be unique."""
        Site.objects.create(name="Same Name", address="123 First St")
        with self.assertRaises(Exception):
            Site.objects.create(name="Same Name", address="456 Second St")


class LeagueModelTest(TestCase):
    """Tests for the League model."""

    def test_league_creation(self):
        """Test creating a league."""
        league = League.objects.create(
            organization="Youth Soccer League",
            assignor="John Doe",
            game_fee=Decimal("75.00"),
            description="Local youth league",
        )
        self.assertEqual(str(league), "Youth Soccer League")
        self.assertEqual(league.game_fee, Decimal("75.00"))

    def test_league_organization_unique(self):
        """Test that organization names must be unique."""
        League.objects.create(
            organization="Same Org", assignor="John", game_fee=Decimal("50.00")
        )
        with self.assertRaises(Exception):
            League.objects.create(
                organization="Same Org", assignor="Jane", game_fee=Decimal("60.00")
            )


class GameModelTest(TestCase):
    """Tests for the Game model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="gametest", password="testpass123"
        )
        self.site = Site.objects.create(
            name="Test Site", address="789 Game St, Nashville, TN"
        )
        self.league = League.objects.create(
            organization="Test League",
            assignor="Test Assignor",
            game_fee=Decimal("50.00"),
        )

    def test_game_creation(self):
        """Test creating a game."""
        game = Game.objects.create(
            user=self.user,
            date=date(2025, 11, 15),
            site=self.site,
            league=self.league,
            mileage=15.5,
            position="Referee",
        )
        self.assertEqual(str(game), "Game on 2025-11-15 at Test Site")
        self.assertEqual(game.mileage, 15.5)
        self.assertFalse(game.fee_paid)
        self.assertFalse(game.mileage_paid)

    def test_game_ordering(self):
        """Test that games are ordered by date."""
        game1 = Game.objects.create(
            user=self.user, date=date(2025, 11, 20), site=self.site, league=self.league
        )
        game2 = Game.objects.create(
            user=self.user, date=date(2025, 11, 10), site=self.site, league=self.league
        )
        game3 = Game.objects.create(
            user=self.user, date=date(2025, 11, 15), site=self.site, league=self.league
        )

        games = list(Game.objects.all())
        self.assertEqual(games[0], game2)
        self.assertEqual(games[1], game3)
        self.assertEqual(games[2], game1)

    def test_game_with_null_site_and_league(self):
        """Test that games can be created without site or league."""
        game = Game.objects.create(user=self.user, date=date(2025, 11, 15), mileage=0.0)
        self.assertIsNone(game.site)
        self.assertIsNone(game.league)


class GameFormTest(TestCase):
    """Tests for the GameForm."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.site = Site.objects.create(
            name="Test Site", address="100 Broadway, Nashville, TN 37203"
        )
        self.league = League.objects.create(
            organization="Test League",
            assignor="Test Assignor",
            game_fee=Decimal("50.00"),
        )

    def test_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            "date": "2025-11-15",
            "site": self.site.id,
            "league": self.league.id,
            "fee_paid": False,
            "mileage_paid": False,
            "mileage": 0.0,
            "position": "Referee",
        }
        form = GameForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_mileage_field_readonly(self):
        """Test that mileage field exists and is in the form."""
        form = GameForm(user=self.user)
        self.assertIn("mileage", form.fields)

    @patch("tracker.forms.distance_miles")
    def test_form_calculates_mileage_on_save(self, mock_distance):
        """Test that form calculates mileage when saving."""
        mock_distance.return_value = 12.5

        form_data = {
            "date": "2025-11-15",
            "site": self.site.id,
            "league": self.league.id,
            "fee_paid": False,
            "mileage_paid": False,
            "mileage": 0.0,
            "position": "Referee",
        }
        form = GameForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

        game = form.save()
        self.assertEqual(game.mileage, 12.5)
        mock_distance.assert_called_once()

    @patch("tracker.forms.distance_miles")
    def test_form_handles_distance_error(self, mock_distance):
        """Test that form handles DistanceError gracefully."""
        mock_distance.side_effect = DistanceError("API error")

        form_data = {
            "date": "2025-11-15",
            "site": self.site.id,
            "league": self.league.id,
            "fee_paid": False,
            "mileage_paid": False,
            "mileage": 0.0,
            "position": "Referee",
        }
        form = GameForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

        game = form.save()
        self.assertEqual(game.mileage, 0.0)

    @patch("tracker.forms.distance_miles")
    def test_form_uses_profile_address_for_mileage(self, mock_distance):
        """Test that form uses user's profile address as origin."""
        self.user.profile.home_address = "456 Oak St"
        self.user.profile.city = "Franklin"
        self.user.profile.state = "TN"
        self.user.profile.zip_code = "37064"
        self.user.profile.save()

        mock_distance.return_value = 15.3

        form_data = {
            "date": "2025-11-15",
            "site": self.site.id,
            "league": self.league.id,
            "fee_paid": False,
            "mileage_paid": False,
            "mileage": 0.0,
            "position": "Referee",
        }
        form = GameForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

        game = form.save()
        self.assertEqual(game.mileage, 15.3)
        # Verify distance_miles was called with profile address as origin
        call_args = mock_distance.call_args[0]
        self.assertEqual(call_args[0], "456 Oak St, Franklin, TN, 37064")


class SiteFormTest(TestCase):
    """Tests for the SiteForm."""

    def test_site_form_valid(self):
        """Test site form with valid data."""
        form_data = {"name": "New Site", "address": "123 New St, Nashville, TN"}
        form = SiteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_site_form_missing_required_fields(self):
        """Test site form with missing required fields."""
        form_data = {"name": "New Site"}
        form = SiteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("address", form.errors)


class LeagueFormTest(TestCase):
    """Tests for the LeagueForm."""

    def test_league_form_valid(self):
        """Test league form with valid data."""
        form_data = {
            "organization": "New League",
            "assignor": "Jane Smith",
            "game_fee": "75.00",
            "description": "Test description",
        }
        form = LeagueForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_league_form_missing_required_fields(self):
        """Test league form with missing required fields."""
        form_data = {"organization": "New League"}
        form = LeagueForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("assignor", form.errors)
        self.assertIn("game_fee", form.errors)


class DistanceMilesTest(TestCase):
    """Tests for the distance_miles utility function."""

    @patch("tracker.utils.googlemaps.Client")
    def test_distance_miles_success(self, mock_client_class):
        """Test successful distance calculation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.distance_matrix.return_value = {
            "rows": [
                {
                    "elements": [
                        {"status": "OK", "distance": {"value": 16093}}  # ~10 miles
                    ]
                }
            ]
        }

        result = distance_miles("Nashville, TN", "Franklin, TN")
        self.assertEqual(result, 10.0)

    @patch("tracker.utils.googlemaps.Client")
    def test_distance_miles_api_error(self, mock_client_class):
        """Test handling of API error status."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.distance_matrix.return_value = {
            "rows": [{"elements": [{"status": "ZERO_RESULTS"}]}]
        }

        with self.assertRaises(DistanceError):
            distance_miles("Invalid Origin", "Invalid Destination")

    @patch("tracker.utils.googlemaps.Client")
    def test_distance_miles_malformed_response(self, mock_client_class):
        """Test handling of malformed API response."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.distance_matrix.return_value = {"rows": []}

        with self.assertRaises(DistanceError):
            distance_miles("Origin", "Destination")


class GameViewsTest(TestCase):
    """Tests for game views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        self.site = Site.objects.create(
            name="Test Site", address="123 Test St, Nashville, TN"
        )
        self.league = League.objects.create(
            organization="Test League",
            assignor="Test Assignor",
            game_fee=Decimal("50.00"),
        )
        self.game = Game.objects.create(
            user=self.user,
            date=date(2025, 11, 15),
            site=self.site,
            league=self.league,
            mileage=10.0,
            position="Referee",
        )

    def test_game_list_view(self):
        """Test game list view."""
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Site")
        self.assertIn("games_by_month", response.context)

    def test_game_list_view_requires_login(self):
        """Test game list view requires authentication."""
        self.client.logout()
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_game_detail_view(self):
        """Test game detail view."""
        response = self.client.get(reverse("game_detail", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("game", response.context)

    def test_game_detail_view_not_found(self):
        """Test game detail view with invalid pk."""
        response = self.client.get(reverse("game_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_game_create_view_get(self):
        """Test game create view GET request."""
        response = self.client.get(reverse("add_game"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @patch("tracker.forms.distance_miles")
    def test_game_create_view_post(self, mock_distance):
        """Test game create view POST request."""
        mock_distance.return_value = 15.0

        data = {
            "date": "2025-11-20",
            "site": self.site.id,
            "league": self.league.id,
            "fee_paid": False,
            "mileage_paid": False,
            "mileage": 0.0,
            "position": "Linesman",
        }
        response = self.client.post(reverse("add_game"), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(Game.objects.count(), 2)

    def test_edit_game_view_get(self):
        """Test edit game view GET request."""
        response = self.client.get(reverse("edit_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @patch("tracker.forms.distance_miles")
    def test_edit_game_view_post(self, mock_distance):
        """Test edit game view POST request."""
        mock_distance.return_value = 20.0

        data = {
            "date": "2025-11-25",
            "site": self.site.id,
            "league": self.league.id,
            "fee_paid": True,
            "mileage_paid": True,
            "mileage": 0.0,
            "position": "Referee",
        }
        response = self.client.post(reverse("edit_game", args=[self.game.pk]), data)
        self.assertEqual(response.status_code, 302)

        self.game.refresh_from_db()
        self.assertTrue(self.game.fee_paid)

    def test_delete_game_view_get(self):
        """Test delete game view GET request shows confirmation."""
        response = self.client.get(reverse("delete_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("game", response.context)
        self.assertEqual(response.context["game"], self.game)

    def test_delete_game_view_post(self):
        """Test delete game view POST request."""
        response = self.client.post(reverse("delete_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Game.objects.count(), 0)


class ProfileViewsTest(TestCase):
    """Tests for profile views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_profile_view_get(self):
        """Test profile view GET request."""
        response = self.client.get(reverse("profile_view"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("profile", response.context)
        self.assertContains(response, "testuser")

    def test_profile_view_requires_login(self):
        """Test profile view requires authentication."""
        self.client.logout()
        response = self.client.get(reverse("profile_view"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_edit_view_get(self):
        """Test profile edit view GET request."""
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("user_form", response.context)
        self.assertIn("profile_form", response.context)

    def test_profile_edit_view_post_updates_email(self):
        """Test profile edit view updates user email."""
        data = {
            "username": "testuser",
            "email": "newemail@example.com",
            "first_name": "",
            "last_name": "",
            "home_address": "",
            "city": "",
            "state": "",
            "zip_code": "",
        }
        response = self.client.post(reverse("profile_edit"), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")

    def test_profile_edit_view_post_updates_profile_info(self):
        """Test profile edit view updates profile information."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "home_address": "123 Main St",
            "city": "Nashville",
            "state": "TN",
            "zip_code": "37203",
        }
        response = self.client.post(reverse("profile_edit"), data)
        self.assertEqual(response.status_code, 302)

        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.first_name, "John")
        self.assertEqual(self.user.profile.last_name, "Doe")
        self.assertEqual(self.user.profile.home_address, "123 Main St")
        self.assertEqual(self.user.profile.city, "Nashville")

    def test_profile_edit_view_requires_login(self):
        """Test profile edit view requires authentication."""
        self.client.logout()
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_display_name_in_view(self):
        """Test that display_name appears correctly in profile view."""
        self.user.profile.first_name = "Jane"
        self.user.profile.last_name = "Smith"
        self.user.profile.save()

        response = self.client.get(reverse("profile_view"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")

    def test_profile_full_address_in_view(self):
        """Test that full address appears correctly in profile view."""
        self.user.profile.home_address = "456 Oak St"
        self.user.profile.city = "Franklin"
        self.user.profile.state = "TN"
        self.user.profile.zip_code = "37064"
        self.user.profile.save()

        response = self.client.get(reverse("profile_view"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "456 Oak St")
        self.assertContains(response, "Franklin")


class ProfileFormTest(TestCase):
    """Tests for the ProfileForm."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_profile_form_valid_data(self):
        """Test profile form with valid data."""
        from tracker.forms import ProfileForm

        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "home_address": "123 Main St",
            "city": "Nashville",
            "state": "TN",
            "zip_code": "37203",
        }
        form = ProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_profile_form_partial_data(self):
        """Test profile form with partial data (all fields optional)."""
        from tracker.forms import ProfileForm

        form_data = {
            "first_name": "John",
            "last_name": "",
            "home_address": "",
            "city": "",
            "state": "",
            "zip_code": "",
        }
        form = ProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_user_form_valid_data(self):
        """Test user form with valid data."""
        from tracker.forms import UserForm

        form_data = {
            "username": "testuser",
            "email": "newemail@example.com",
        }
        form = UserForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_user_form_invalid_email(self):
        """Test user form with invalid email."""
        from tracker.forms import UserForm

        form_data = {
            "username": "testuser",
            "email": "invalid-email",
        }
        form = UserForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class HomeViewTest(TestCase):
    """Tests for home view."""

    def test_home_view(self):
        """Test home view GET request."""
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")


class ProfileEditErrorHandlingTest(TestCase):
    """Tests for profile edit error handling."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

    def test_profile_edit_invalid_form_shows_error(self):
        """Test profile edit view shows error message with invalid data."""
        data = {
            "username": "testuser",
            "email": "invalid-email-format",  # Invalid email
            "first_name": "John",
            "last_name": "Doe",
            "home_address": "",
            "city": "",
            "state": "",
            "zip_code": "",
        }
        response = self.client.post(reverse("profile_edit"), data)
        self.assertEqual(response.status_code, 200)  # Should re-render form
        messages_list = list(response.context["messages"])
        self.assertTrue(any("error" in str(m).lower() for m in messages_list))


class GameListPostTest(TestCase):
    """Tests for game list POST handling."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        self.site = Site.objects.create(
            name="Test Site", address="123 Test St, Nashville, TN"
        )
        self.league = League.objects.create(
            organization="Test League",
            assignor="Test Assignor",
            game_fee=Decimal("50.00"),
        )

    @patch("tracker.forms.distance_miles")
    def test_game_list_post_creates_game(self, mock_distance):
        """Test posting to game list creates a game."""
        mock_distance.return_value = 10.0

        data = {
            "date": "2025-12-15",
            "site": self.site.id,
            "league": self.league.id,
            "fee_paid": False,
            "mileage_paid": False,
            "mileage": 0.0,
            "position": "Referee",
        }
        response = self.client.post(reverse("game_list"), data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Game.objects.count(), 1)


class TripMileageAggregationTest(TestCase):
    """Tests for trip-based mileage aggregation (issue #94)."""

    def setUp(self):
        """Create a user, two sites, and two leagues sharing an assignor."""
        self.user = User.objects.create_user(
            username="tripuser", password="testpass123"
        )
        self.site_a = Site.objects.create(name="Site A", address="1 A St")
        self.site_b = Site.objects.create(name="Site B", address="2 B St")
        self.league = League.objects.create(
            organization="League One", assignor="Pat", game_fee=Decimal("50.00")
        )
        self.other_league = League.objects.create(
            organization="League Two", assignor="Pat", game_fee=Decimal("60.00")
        )
        self.game_date = date(2026, 4, 1)

    def _game(self, site, mileage, league=None, game_date=None, position=""):
        """Create a game owned by the test user."""
        return Game.objects.create(
            user=self.user,
            date=game_date or self.game_date,
            site=site,
            league=league or self.league,
            mileage=mileage,
            position=position,
        )

    def test_mileage_by_collapses_games_at_one_site_on_one_date(self):
        """Three games at one site on one date count the trip once."""
        for position in ("PU", "U1", "U3"):
            self._game(self.site_a, 20.0, position=position)
        totals = mileage_by(Game.objects.all(), lambda g: g.site.name)
        self.assertEqual(totals["Site A"], 20.0)

    def test_mileage_by_counts_separate_sites_on_one_date(self):
        """Two sites on the same date are two trips."""
        self._game(self.site_a, 20.0)
        self._game(self.site_b, 30.0)
        totals = mileage_by(Game.objects.all(), lambda g: g.site.name)
        self.assertEqual(totals["Site A"], 20.0)
        self.assertEqual(totals["Site B"], 30.0)

    def test_mileage_by_counts_same_site_on_separate_dates(self):
        """The same site on two dates is two trips."""
        self._game(self.site_a, 20.0)
        self._game(self.site_a, 20.0, game_date=date(2026, 4, 8))
        totals = mileage_by(Game.objects.all(), lambda g: g.site.name)
        self.assertEqual(totals["Site A"], 40.0)

    def test_mileage_by_uses_largest_value_in_a_trip(self):
        """A trip takes the largest mileage recorded against its games."""
        self._game(self.site_a, 0.0)
        self._game(self.site_a, 25.0)
        totals = mileage_by(Game.objects.all(), lambda g: g.site.name)
        self.assertEqual(totals["Site A"], 25.0)

    def test_mileage_by_handles_zero_and_missing_mileage(self):
        """Zero mileage yields a zero total rather than an absent group."""
        self._game(self.site_a, 0.0)
        totals = mileage_by(Game.objects.all(), lambda g: g.site.name)
        self.assertEqual(totals["Site A"], 0.0)

    def test_mileage_by_groups_games_with_no_site(self):
        """Games with no site group under None without raising."""
        Game.objects.create(
            user=self.user, date=self.game_date, site=None, mileage=12.0
        )
        totals = mileage_by(
            Game.objects.all(), lambda g: g.site.name if g.site else None
        )
        self.assertEqual(totals[None], 12.0)

    def test_total_mileage_counts_each_trip_once(self):
        """The overall total deduplicates trips across all groups."""
        for position in ("PU", "U1"):
            self._game(self.site_a, 20.0, position=position)
        self._game(self.site_b, 30.0)
        self.assertEqual(total_mileage(Game.objects.all()), 50.0)

    def test_total_mileage_of_no_games_is_zero(self):
        """An empty set of games totals zero."""
        self.assertEqual(total_mileage(Game.objects.none()), 0.0)

    def test_stats_view_mileage_counts_trip_once_per_breakdown(self):
        """Year, league, assignor, and site each count a shared trip once."""
        for position in ("PU", "U1", "U3"):
            self._game(self.site_a, 20.0, position=position)
        client = Client()
        client.login(username="tripuser", password="testpass123")
        response = client.get(reverse("game_stats"))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["by_year"][0]["total_mileage"], 20.0)
        self.assertEqual(response.context["by_league"][0]["total_mileage"], 20.0)
        self.assertEqual(response.context["by_assignor"][0]["total_mileage"], 20.0)
        self.assertEqual(response.context["by_site"][0]["total_mileage"], 20.0)
        # The game count still reflects every game worked.
        self.assertEqual(response.context["by_site"][0]["count"], 3)

    def test_stats_site_breakdown_totals_match_year_breakdown(self):
        """Site mileage sums to the same figure as the year breakdown."""
        for position in ("PU", "U1"):
            self._game(self.site_a, 20.0, position=position)
        self._game(self.site_b, 30.0)
        client = Client()
        client.login(username="tripuser", password="testpass123")
        response = client.get(reverse("game_stats"))

        site_total = sum(row["total_mileage"] for row in response.context["by_site"])
        year_total = sum(row["total_mileage"] for row in response.context["by_year"])
        self.assertEqual(site_total, 50.0)
        self.assertEqual(site_total, year_total)

    def test_stats_position_breakdown_has_no_mileage(self):
        """Position rows carry no mileage, since a trip spans positions."""
        self._game(self.site_a, 20.0, position="PU")
        client = Client()
        client.login(username="tripuser", password="testpass123")
        response = client.get(reverse("game_stats"))
        for row in response.context["by_position"]:
            self.assertNotIn("total_mileage", row)

    def test_stats_shared_trip_counts_once_per_league(self):
        """Two leagues at one site on one date each carry the trip."""
        self._game(self.site_a, 20.0, league=self.league)
        self._game(self.site_a, 20.0, league=self.other_league)
        client = Client()
        client.login(username="tripuser", password="testpass123")
        response = client.get(reverse("game_stats"))

        by_league = {
            row["league__organization"]: row["total_mileage"]
            for row in response.context["by_league"]
        }
        self.assertEqual(by_league["League One"], 20.0)
        self.assertEqual(by_league["League Two"], 20.0)
        # The trip itself was driven once, so the year total counts it once.
        self.assertEqual(response.context["by_year"][0]["total_mileage"], 20.0)

    def test_game_list_summary_mileage_counts_trip_once(self):
        """The game list mileage tile matches the trip rows it renders."""
        for position in ("PU", "U1", "U3"):
            self._game(self.site_a, 20.0, position=position)
        client = Client()
        client.login(username="tripuser", password="testpass123")
        response = client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"]["total_mileage"], 20.0)

    def test_game_list_summary_mileage_matches_trip_rows(self):
        """The tile equals the sum of the per-trip values shown in the table."""
        for position in ("PU", "U1"):
            self._game(self.site_a, 20.0, position=position)
        self._game(self.site_b, 30.0)
        client = Client()
        client.login(username="tripuser", password="testpass123")
        response = client.get(reverse("game_list"))

        rendered_trips = sum(
            trip_mileage
            for _, date_site_groups, _ in response.context["games_by_month"]
            for _, _, trip_mileage, _, _ in date_site_groups
        )
        self.assertEqual(response.context["summary"]["total_mileage"], rendered_trips)
        self.assertEqual(rendered_trips, 50.0)


class ResolveOriginTest(TestCase):
    """Tests for origin address resolution (issue #95)."""

    def setUp(self):
        """Create a user whose profile has no address set."""
        self.user = User.objects.create_user(
            username="originuser", password="testpass123"
        )

    def test_structured_address_is_preferred(self):
        """A populated profile address wins over the configured default."""
        profile = self.user.profile
        profile.home_address = "100 Main St"
        profile.city = "Nashville"
        profile.state = "TN"
        profile.zip_code = "37201"
        profile.save()
        self.assertEqual(resolve_origin(self.user), "100 Main St, Nashville, TN, 37201")

    def test_empty_profile_falls_back_to_default(self):
        """A profile with no address falls back to the configured default."""
        self.assertEqual(resolve_origin(self.user), settings.DEFAULT_ADDRESS)

    def test_legacy_location_is_used_when_structured_fields_empty(self):
        """The legacy location field still serves as a fallback."""
        profile = self.user.profile
        profile.location = "Legacy Address"
        profile.save()
        self.assertEqual(resolve_origin(self.user), "Legacy Address")

    def test_user_without_profile_falls_back_to_default(self):
        """A user with no related profile does not raise."""
        self.assertEqual(resolve_origin(None), settings.DEFAULT_ADDRESS)


class SiteDistanceOriginTest(TestCase):
    """The mileage preview and the saved mileage must agree (issue #95)."""

    def setUp(self):
        """Create a user with a structured address and an empty legacy field."""
        self.user = User.objects.create_user(
            username="previewuser", password="testpass123"
        )
        profile = self.user.profile
        profile.home_address = "100 Main St"
        profile.city = "Nashville"
        profile.state = "TN"
        profile.zip_code = "37201"
        profile.location = ""
        profile.save()
        self.site = Site.objects.create(name="Preview Site", address="500 Far Rd")
        self.league = League.objects.create(
            organization="Preview League", assignor="Pat", game_fee=Decimal("50.00")
        )
        self.client = Client()
        self.client.login(username="previewuser", password="testpass123")

    @patch("tracker.views.distance_miles")
    def test_preview_uses_structured_address_not_legacy_field(self, mock_distance):
        """The preview calculates from full_address when location is empty."""
        mock_distance.return_value = 42.0
        response = self.client.get(reverse("site_distance"), {"site": self.site.pk})
        self.assertEqual(response.status_code, 200)
        mock_distance.assert_called_once_with(
            "100 Main St, Nashville, TN, 37201", "500 Far Rd"
        )
        self.assertIn("42.0", response.content.decode())

    @patch("tracker.views.distance_miles")
    @patch("tracker.forms.distance_miles")
    def test_preview_and_saved_mileage_use_the_same_origin(
        self, mock_form_distance, mock_view_distance
    ):
        """Both paths resolve the same origin for the same site."""
        mock_view_distance.return_value = 42.0
        mock_form_distance.return_value = 42.0

        self.client.get(reverse("site_distance"), {"site": self.site.pk})
        form = GameForm(
            data={
                "date": "2026-04-01",
                "site": self.site.pk,
                "league": self.league.pk,
                "position": "PU",
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        game = form.save()

        self.assertEqual(
            mock_view_distance.call_args.args, mock_form_distance.call_args.args
        )
        self.assertEqual(game.mileage, 42.0)

    @patch("tracker.views.distance_miles")
    def test_preview_falls_back_to_default_address(self, mock_distance):
        """With no profile address, the preview uses the configured default."""
        profile = self.user.profile
        profile.home_address = ""
        profile.city = ""
        profile.state = ""
        profile.zip_code = ""
        profile.save()
        mock_distance.return_value = 5.0
        self.client.get(reverse("site_distance"), {"site": self.site.pk})
        mock_distance.assert_called_once_with(settings.DEFAULT_ADDRESS, "500 Far Rd")

    @patch("tracker.views.distance_miles")
    def test_preview_returns_zero_on_distance_error(self, mock_distance):
        """A failed lookup still yields zero miles, as before."""
        mock_distance.side_effect = DistanceError("boom")
        response = self.client.get(reverse("site_distance"), {"site": self.site.pk})
        self.assertEqual(response.status_code, 200)
        self.assertIn("0", response.content.decode())


class DistanceClientFailureTest(TestCase):
    """The Maps client failing is reported as a DistanceError."""

    @patch("tracker.utils.googlemaps.Client")
    def test_client_construction_failure_raises_distance_error(self, mock_client_class):
        """A transport or credential failure surfaces as DistanceError."""
        mock_client_class.side_effect = RuntimeError("no network")
        with self.assertRaises(DistanceError):
            distance_miles("Origin", "Destination")


class ToggleFeePaidTest(TestCase):
    """Tests for the fee_paid toggle endpoint."""

    def setUp(self):
        """Create a logged-in owner with one unpaid game."""
        self.user = User.objects.create_user(username="owner", password="testpass123")
        self.client.login(username="owner", password="testpass123")
        self.site = Site.objects.create(name="Toggle Site", address="1 Toggle Way")
        self.league = League.objects.create(
            organization="Toggle League",
            assignor="Toggle Assignor",
            game_fee=Decimal("40.00"),
        )
        self.game = Game.objects.create(
            user=self.user,
            date=date(2025, 5, 1),
            site=self.site,
            league=self.league,
            fee_paid=False,
        )

    def test_toggle_marks_an_unpaid_game_paid(self):
        """An unpaid game becomes paid and the new state is returned."""
        response = self.client.post(reverse("toggle_fee_paid", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"fee_paid": True})
        self.game.refresh_from_db()
        self.assertTrue(self.game.fee_paid)

    def test_toggle_marks_a_paid_game_unpaid(self):
        """The toggle reverses in both directions, not just to paid."""
        self.game.fee_paid = True
        self.game.save(update_fields=["fee_paid"])
        response = self.client.post(reverse("toggle_fee_paid", args=[self.game.pk]))
        self.assertEqual(response.json(), {"fee_paid": False})
        self.game.refresh_from_db()
        self.assertFalse(self.game.fee_paid)

    def test_toggle_leaves_other_fields_untouched(self):
        """Only fee_paid is written, so a concurrent mileage edit survives."""
        Game.objects.filter(pk=self.game.pk).update(mileage=33.0)
        self.client.post(reverse("toggle_fee_paid", args=[self.game.pk]))
        self.game.refresh_from_db()
        self.assertEqual(self.game.mileage, 33.0)

    def test_get_is_rejected(self):
        """The toggle mutates state, so GET is not allowed."""
        response = self.client.get(reverse("toggle_fee_paid", args=[self.game.pk]))
        self.assertEqual(response.status_code, 405)
        self.game.refresh_from_db()
        self.assertFalse(self.game.fee_paid)

    def test_toggle_requires_login(self):
        """An anonymous POST is redirected and changes nothing."""
        self.client.logout()
        response = self.client.post(reverse("toggle_fee_paid", args=[self.game.pk]))
        self.assertEqual(response.status_code, 302)
        self.game.refresh_from_db()
        self.assertFalse(self.game.fee_paid)

    def test_toggle_of_missing_game_is_404(self):
        """A pk that does not exist is a 404, not a 500."""
        response = self.client.post(reverse("toggle_fee_paid", args=[99999]))
        self.assertEqual(response.status_code, 404)


class FeeAggregationTest(TestCase):
    """Tests for the effective-fee rollups on the game list and stats pages.

    The effective fee of a game is its own ``fee`` when set and its league's
    ``game_fee`` otherwise. These tests fix that fallback, and fix which games
    each total includes, so the rules cannot be changed unnoticed.
    """

    def setUp(self):
        """Build one league fee game, one overridden fee game, one volunteer."""
        self.user = User.objects.create_user(username="fees", password="testpass123")
        self.client.login(username="fees", password="testpass123")
        self.site = Site.objects.create(name="Fee Site", address="1 Fee Rd")
        self.league = League.objects.create(
            organization="Fee League",
            assignor="Fee Assignor",
            game_fee=Decimal("50.00"),
        )
        # Falls back to the league fee of 50, and is owed.
        self.unpaid = Game.objects.create(
            user=self.user,
            date=date(2025, 3, 1),
            site=self.site,
            league=self.league,
            fee=None,
            fee_paid=False,
        )
        # Overrides the league fee with 75, and has been paid.
        self.paid = Game.objects.create(
            user=self.user,
            date=date(2025, 3, 2),
            site=self.site,
            league=self.league,
            fee=Decimal("75.00"),
            fee_paid=True,
        )
        # Worked for free: carries a fee on paper but is never owed.
        self.volunteer = Game.objects.create(
            user=self.user,
            date=date(2025, 3, 3),
            site=self.site,
            league=self.league,
            fee=None,
            fee_paid=False,
            is_volunteer=True,
        )

    def summary(self):
        """The game list summary dict for the logged-in user."""
        return self.client.get(reverse("game_list")).context["summary"]

    def test_total_fees_sums_effective_fees(self):
        """50 from the league fee, 75 from the override, 50 for the volunteer."""
        self.assertEqual(self.summary()["total_fees"], Decimal("175.00"))

    def test_league_fee_is_used_when_the_game_has_none(self):
        """A game with no fee of its own is worth its league's game fee."""
        self.paid.delete()
        self.volunteer.delete()
        self.assertEqual(self.summary()["total_fees"], Decimal("50.00"))

    def test_game_fee_overrides_the_league_fee(self):
        """A game that sets its own fee ignores the league fee entirely."""
        self.unpaid.delete()
        self.volunteer.delete()
        self.assertEqual(self.summary()["total_fees"], Decimal("75.00"))

    def test_a_game_with_no_fee_and_no_league_contributes_nothing(self):
        """With neither source of a fee there is no effective fee to add."""
        Game.objects.all().delete()
        Game.objects.create(
            user=self.user, date=date(2025, 3, 4), site=self.site, league=None, fee=None
        )
        self.assertIsNone(self.summary()["total_fees"])

    def test_paid_fees_counts_only_games_marked_paid(self):
        """Received income is the paid games alone."""
        self.assertEqual(self.summary()["paid_fees"], Decimal("75.00"))

    def test_unpaid_fees_excludes_volunteer_games(self):
        """A volunteer game is unpaid but is not owed, so it is not counted.

        Without the is_volunteer filter this would be 100.00.
        """
        self.assertEqual(self.summary()["unpaid_fees"], Decimal("50.00"))

    def test_volunteer_games_still_count_toward_total_fees(self):
        """Volunteer work is excluded from money owed, not from the total."""
        summary = self.summary()
        self.assertEqual(summary["total_fees"], Decimal("175.00"))
        self.assertEqual(summary["count"], 3)

    def test_stats_year_totals_match_the_list_summary(self):
        """The two pages aggregate the same games the same way."""
        summary = self.summary()
        row = self.client.get(reverse("game_stats")).context["by_year"][0]
        self.assertEqual(row["year"], 2025)
        self.assertEqual(row["count"], summary["count"])
        self.assertEqual(row["total_fees"], summary["total_fees"])
        self.assertEqual(row["paid_fees"], summary["paid_fees"])
        self.assertEqual(row["unpaid_fees"], summary["unpaid_fees"])

    def test_stats_breakdowns_exclude_volunteer_games_from_unpaid(self):
        """Every stats breakdown applies the volunteer rule, not just by_year."""
        context = self.client.get(reverse("game_stats")).context
        for key in ("by_year", "by_league", "by_assignor", "by_position", "by_site"):
            with self.subTest(breakdown=key):
                owed = sum(row["unpaid_fees"] or 0 for row in context[key])
                self.assertEqual(owed, Decimal("50.00"))


class UserIsolationTest(TestCase):
    """One user must never read or write another user's games.

    Every view filters by ``user=request.user``. These tests fail if any of
    those filters is dropped, which a lookup by a nonexistent pk would not
    catch.
    """

    def setUp(self):
        """Give the owner a game, then log in as a different user."""
        self.owner = User.objects.create_user(username="owner", password="testpass123")
        self.intruder = User.objects.create_user(
            username="intruder", password="testpass123"
        )
        self.site = Site.objects.create(name="Private Site", address="1 Private Ln")
        self.league = League.objects.create(
            organization="Private League",
            assignor="Private Assignor",
            game_fee=Decimal("60.00"),
        )
        self.game = Game.objects.create(
            user=self.owner,
            date=date(2025, 7, 4),
            site=self.site,
            league=self.league,
            mileage=25.0,
            position="Referee",
        )
        self.client.login(username="intruder", password="testpass123")

    def test_detail_of_another_users_game_is_404(self):
        """Reading someone else's game is refused."""
        response = self.client.get(reverse("game_detail", args=[self.game.pk]))
        self.assertEqual(response.status_code, 404)

    def test_edit_form_for_another_users_game_is_404(self):
        """The edit form is not served for someone else's game."""
        response = self.client.get(reverse("edit_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 404)

    def test_edit_post_to_another_users_game_is_404(self):
        """A crafted POST cannot overwrite someone else's game."""
        response = self.client.post(
            reverse("edit_game", args=[self.game.pk]),
            {
                "date": "2030-01-01",
                "site": self.site.pk,
                "league": self.league.pk,
                "mileage": 0.0,
                "position": "Stolen",
            },
        )
        self.assertEqual(response.status_code, 404)
        self.game.refresh_from_db()
        self.assertEqual(self.game.position, "Referee")

    def test_delete_post_for_another_users_game_is_404(self):
        """A crafted POST cannot delete someone else's game."""
        response = self.client.post(reverse("delete_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Game.objects.filter(pk=self.game.pk).exists())

    def test_toggle_on_another_users_game_is_404(self):
        """A crafted POST cannot mark someone else's game paid."""
        response = self.client.post(reverse("toggle_fee_paid", args=[self.game.pk]))
        self.assertEqual(response.status_code, 404)
        self.game.refresh_from_db()
        self.assertFalse(self.game.fee_paid)

    def test_game_list_hides_another_users_games(self):
        """The list shows no rows, no totals, and no filter options."""
        context = self.client.get(reverse("game_list")).context
        self.assertEqual(context["games_by_month"], [])
        self.assertEqual(context["summary"]["count"], 0)
        self.assertEqual(context["summary"]["total_mileage"], 0)
        self.assertEqual(context["available_sites"], [])

    def test_stats_hide_another_users_games(self):
        """Every stats breakdown is empty for a user with no games."""
        context = self.client.get(reverse("game_stats")).context
        for key in ("by_year", "by_league", "by_assignor", "by_position", "by_site"):
            with self.subTest(breakdown=key):
                self.assertEqual(list(context[key]), [])

    def test_a_new_game_is_owned_by_its_creator(self):
        """Saving through the form attaches the game to the logged-in user."""
        with patch("tracker.forms.distance_miles", return_value=5.0):
            self.client.post(
                reverse("add_game"),
                {
                    "date": "2025-08-01",
                    "site": self.site.pk,
                    "league": self.league.pk,
                    "mileage": 0.0,
                    "position": "Umpire",
                },
            )
        created = Game.objects.get(position="Umpire")
        self.assertEqual(created.user, self.intruder)


class GameListFilterOptionsTest(TestCase):
    """Tests for the filter dropdown options built by the game list view."""

    def setUp(self):
        """Create games across two years, two leagues, and three sites."""
        self.user = User.objects.create_user(username="filters", password="testpass123")
        self.client.login(username="filters", password="testpass123")
        self.alpha = Site.objects.create(name="Alpha Field", address="1 Alpha St")
        self.bravo = Site.objects.create(name="Bravo Field", address="2 Bravo St")
        self.zulu = Site.objects.create(name="Zulu Field", address="3 Zulu St")
        self.east = League.objects.create(
            organization="East League",
            assignor="Quinn",
            game_fee=Decimal("45.00"),
        )
        self.west = League.objects.create(
            organization="West League",
            assignor="Avery",
            game_fee=Decimal("55.00"),
        )
        Game.objects.create(
            user=self.user,
            date=date(2024, 4, 1),
            site=self.zulu,
            league=self.west,
            position="U1",
        )
        Game.objects.create(
            user=self.user,
            date=date(2025, 4, 1),
            site=self.alpha,
            league=self.east,
            position="PU",
        )
        # A second 2025 game in the same league, to prove the lists de-duplicate.
        Game.objects.create(
            user=self.user,
            date=date(2025, 5, 1),
            site=self.bravo,
            league=self.east,
            position="PU",
        )

    def context(self):
        """The game list context for the logged-in user."""
        return self.client.get(reverse("game_list")).context

    def test_years_are_distinct_and_newest_first(self):
        """The year filter lists each year once, most recent at the top."""
        self.assertEqual(self.context()["available_years"], [2025, 2024])

    def test_leagues_are_distinct_and_alphabetical(self):
        """Two games in one league produce one league option."""
        self.assertEqual(
            self.context()["available_leagues"], ["East League", "West League"]
        )

    def test_assignors_are_distinct_and_alphabetical(self):
        """Assignors sort by name, not by the league they assign for."""
        self.assertEqual(self.context()["available_assignors"], ["Avery", "Quinn"])

    def test_sites_are_distinct_and_alphabetical(self):
        """Every site worked appears once, in name order."""
        self.assertEqual(
            self.context()["available_sites"],
            ["Alpha Field", "Bravo Field", "Zulu Field"],
        )

    def test_positions_are_distinct_and_alphabetical(self):
        """Two games in one position produce one position option."""
        self.assertEqual(self.context()["available_positions"], ["PU", "U1"])

    def test_blank_and_missing_positions_are_not_offered(self):
        """A game with no position must not add an empty filter option."""
        Game.objects.create(
            user=self.user, date=date(2025, 6, 1), site=self.alpha, position=""
        )
        Game.objects.create(
            user=self.user, date=date(2025, 6, 2), site=self.alpha, position=None
        )
        self.assertEqual(self.context()["available_positions"], ["PU", "U1"])

    def test_games_with_no_league_do_not_add_blank_options(self):
        """A leagueless game leaves the league and assignor lists unchanged."""
        Game.objects.create(
            user=self.user, date=date(2025, 7, 1), site=self.alpha, league=None
        )
        context = self.context()
        self.assertEqual(context["available_leagues"], ["East League", "West League"])
        self.assertEqual(context["available_assignors"], ["Avery", "Quinn"])


class TripGroupingTest(TestCase):
    """Tests for how the game list groups games into trips and months."""

    def setUp(self):
        """Create a logged-in user and a pair of sites."""
        self.user = User.objects.create_user(username="trips", password="testpass123")
        self.client.login(username="trips", password="testpass123")
        self.home_field = Site.objects.create(name="Home Field", address="1 Home St")
        self.away_field = Site.objects.create(name="Away Field", address="2 Away St")

    def add_game(self, day, site, mileage=12.0, mileage_paid=False):
        """Create one game for the logged-in user in May 2025."""
        return Game.objects.create(
            user=self.user,
            date=date(2025, 5, day),
            site=site,
            mileage=mileage,
            mileage_paid=mileage_paid,
        )

    def trips(self):
        """Flatten every month's trip rows into one list."""
        context = self.client.get(reverse("game_list")).context
        return [
            trip
            for _, date_site_groups, _ in context["games_by_month"]
            for trip in date_site_groups
        ]

    def test_games_at_one_site_on_one_date_become_one_trip(self):
        """Two games at the same place on the same day are a single drive."""
        self.add_game(1, self.home_field)
        self.add_game(1, self.home_field)
        trips = self.trips()
        self.assertEqual(len(trips), 1)
        self.assertEqual(len(trips[0][4]), 2)

    def test_two_sites_on_one_date_are_two_trips(self):
        """Driving to a second site that day is a second trip."""
        self.add_game(1, self.home_field)
        self.add_game(1, self.away_field)
        self.assertEqual(len(self.trips()), 2)

    def test_a_trip_reports_the_largest_mileage_of_its_games(self):
        """The trip distance is the longest recorded leg, not their sum."""
        self.add_game(1, self.home_field, mileage=12.0)
        self.add_game(1, self.home_field, mileage=18.0)
        self.assertEqual(self.trips()[0][2], 18.0)

    def test_a_trip_is_paid_only_when_every_game_in_it_is_paid(self):
        """Reimbursement for one game of a trip does not settle the trip."""
        self.add_game(1, self.home_field, mileage_paid=True)
        self.add_game(1, self.home_field, mileage_paid=False)
        self.assertFalse(self.trips()[0][3])

    def test_a_trip_is_paid_when_all_of_its_games_are_paid(self):
        """With every game reimbursed the trip reads as paid."""
        self.add_game(1, self.home_field, mileage_paid=True)
        self.add_game(1, self.home_field, mileage_paid=True)
        self.assertTrue(self.trips()[0][3])

    def test_a_zero_mileage_trip_is_never_paid(self):
        """There is nothing to reimburse for a trip of no distance."""
        self.add_game(1, self.home_field, mileage=0.0, mileage_paid=True)
        self.assertFalse(self.trips()[0][3])

    def test_a_game_with_no_site_shows_a_blank_site_name(self):
        """A siteless game still groups, with an empty name rather than None."""
        Game.objects.create(user=self.user, date=date(2025, 5, 1), site=None)
        self.assertEqual(self.trips()[0][1], "")

    def test_months_carry_a_label_and_a_game_count(self):
        """Each month reports how many games it holds, not how many trips."""
        self.add_game(1, self.home_field)
        self.add_game(1, self.home_field)
        context = self.client.get(reverse("game_list")).context
        label, _, count = context["games_by_month"][0]
        self.assertEqual(label, "May 2025")
        self.assertEqual(count, 2)

    def test_the_most_recent_month_is_expanded(self):
        """The list opens on the latest month a game was worked."""
        self.add_game(1, self.home_field)
        Game.objects.create(
            user=self.user, date=date(2025, 9, 20), site=self.away_field
        )
        context = self.client.get(reverse("game_list")).context
        self.assertEqual(context["expand_month"], "September 2025")

    def test_a_user_with_no_games_expands_the_current_month(self):
        """With nothing to show the list opens on today's month."""
        context = self.client.get(reverse("game_list")).context
        self.assertEqual(context["games_by_month"], [])
        self.assertEqual(context["expand_month"], date.today().strftime("%B %Y"))


class GameFormEditTest(TestCase):
    """Tests for how GameForm behaves on an existing game.

    Creating a game always recalculates mileage. Editing one must not discard a
    distance the user typed in by hand.
    """

    def setUp(self):
        """Create a saved game with no fee of its own."""
        self.user = User.objects.create_user(username="editor", password="testpass123")
        self.site = Site.objects.create(name="Edit Site", address="1 Edit Rd")
        self.league = League.objects.create(
            organization="Edit League",
            assignor="Edit Assignor",
            game_fee=Decimal("65.00"),
        )
        self.game = Game.objects.create(
            user=self.user,
            date=date(2025, 2, 10),
            site=self.site,
            league=self.league,
            fee=None,
            mileage=30.0,
            position="Referee",
        )

    def post_data(self, **overrides):
        """Form data that resubmits the saved game, with optional changes."""
        data = {
            "date": "2025-02-10",
            "site": self.site.pk,
            "league": self.league.pk,
            "mileage": 30.0,
            "position": "Referee",
        }
        data.update(overrides)
        return data

    def test_the_league_fee_prefills_a_game_with_no_fee(self):
        """Editing shows what the game is worth instead of an empty box."""
        form = GameForm(instance=self.game, user=self.user)
        self.assertEqual(form.initial["fee"], Decimal("65.00"))

    def test_an_existing_fee_is_not_replaced_by_the_league_fee(self):
        """A fee the user already set survives a trip through the form."""
        self.game.fee = Decimal("90.00")
        self.game.save(update_fields=["fee"])
        form = GameForm(instance=self.game, user=self.user)
        self.assertEqual(form.initial["fee"], Decimal("90.00"))

    def test_a_game_with_no_league_is_not_prefilled(self):
        """With no league there is no fee to fall back on."""
        self.game.league = None
        self.game.save(update_fields=["league"])
        form = GameForm(instance=self.game, user=self.user)
        self.assertIsNone(form.initial.get("fee"))

    def test_mileage_is_editable_with_help_text_when_editing(self):
        """Editing exposes mileage so a user can correct it."""
        form = GameForm(instance=self.game, user=self.user)
        self.assertNotIsInstance(form.fields["mileage"].widget, forms.HiddenInput)
        self.assertIn("recalculate", form.fields["mileage"].help_text)

    def test_mileage_is_hidden_and_optional_when_creating(self):
        """A new game calculates its own mileage, so the field is hidden."""
        form = GameForm(user=self.user)
        self.assertIsInstance(form.fields["mileage"].widget, forms.HiddenInput)
        self.assertFalse(form.fields["mileage"].required)

    @patch("tracker.forms.distance_miles")
    def test_a_hand_edited_mileage_is_kept(self, mock_distance):
        """A typed distance is not overwritten by the Maps lookup."""
        mock_distance.return_value = 99.0
        form = GameForm(
            self.post_data(mileage=42.5), instance=self.game, user=self.user
        )
        self.assertTrue(form.is_valid(), form.errors)
        game = form.save()
        self.assertEqual(game.mileage, 42.5)
        mock_distance.assert_not_called()

    @patch("tracker.forms.distance_miles")
    def test_an_untouched_mileage_is_recalculated(self, mock_distance):
        """Leaving mileage alone refreshes it, which is what the help text says."""
        mock_distance.return_value = 99.0
        form = GameForm(self.post_data(), instance=self.game, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        game = form.save()
        self.assertEqual(game.mileage, 99.0)
        mock_distance.assert_called_once()

    @patch("tracker.forms.distance_miles")
    def test_a_failed_lookup_on_edit_zeroes_the_mileage(self, mock_distance):
        """A recalculation that cannot reach the API falls back to zero."""
        mock_distance.side_effect = DistanceError("boom")
        form = GameForm(self.post_data(), instance=self.game, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().mileage, 0.0)

    def test_saving_without_a_user_leaves_the_owner_alone(self):
        """GameForm is usable without a user, as the mileage preview does."""
        with patch("tracker.forms.distance_miles", return_value=7.0):
            game = GameForm(self.post_data(), instance=self.game).save()
        self.assertEqual(game.user, self.user)


class LoginRequiredTest(TestCase):
    """Every view that touches a user's data must demand a login."""

    def setUp(self):
        """Create a game to address, but do not log anybody in."""
        user = User.objects.create_user(username="absent", password="testpass123")
        site = Site.objects.create(name="Closed Site", address="1 Closed Way")
        self.game = Game.objects.create(user=user, date=date(2025, 1, 1), site=site)

    def test_protected_views_redirect_anonymous_visitors(self):
        """An anonymous GET is redirected to the login page, not served."""
        urls = [
            reverse("game_list"),
            reverse("game_stats"),
            reverse("add_game"),
            reverse("profile_view"),
            reverse("profile_edit"),
            reverse("site_distance"),
            reverse("game_detail", args=[self.game.pk]),
            reverse("edit_game", args=[self.game.pk]),
            reverse("delete_game", args=[self.game.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(settings.LOGIN_URL, response["Location"])

    def test_the_home_page_is_public(self):
        """The landing page is reachable without an account."""
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
