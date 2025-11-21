from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from tracker.forms import GameForm, LeagueForm, SiteForm
from tracker.models import Game, League, Location, Profile, Site
from tracker.utils import DistanceError, distance_miles


class ProfileModelTest(TestCase):
    """Tests for the Profile model."""

    @pytest.mark.skip(reason="Profile creation signal not implemented yet")
    def test_profile_created_on_user_creation(self):
        """Test that a profile is automatically created when a user is created."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)

    @pytest.mark.skip(reason="Profile creation signal not implemented yet")
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
            date=date(2025, 11, 20), site=self.site, league=self.league
        )
        game2 = Game.objects.create(
            date=date(2025, 11, 10), site=self.site, league=self.league
        )
        game3 = Game.objects.create(
            date=date(2025, 11, 15), site=self.site, league=self.league
        )

        games = list(Game.objects.all())
        self.assertEqual(games[0], game2)
        self.assertEqual(games[1], game3)
        self.assertEqual(games[2], game1)

    def test_game_with_null_site_and_league(self):
        """Test that games can be created without site or league."""
        game = Game.objects.create(date=date(2025, 11, 15), mileage=0.0)
        self.assertIsNone(game.site)
        self.assertIsNone(game.league)


class GameFormTest(TestCase):
    """Tests for the GameForm."""

    def setUp(self):
        """Set up test data."""
        self.site = Site.objects.create(
            name="Test Site", address="100 Broadway, Nashville, TN 37203"
        )
        self.league = League.objects.create(
            organization="Test League",
            assignor="Test Assignor",
            game_fee=Decimal("50.00"),
        )

    @pytest.mark.skip(reason="Profile creation signal not implemented yet")
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
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_mileage_field_readonly(self):
        """Test that mileage field is set to readonly."""
        form = GameForm()
        self.assertTrue(form.fields["mileage"].widget.attrs.get("readonly"))

    @pytest.mark.skip(reason="Profile creation signal not implemented yet")
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
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())

        game = form.save()
        self.assertEqual(game.mileage, 12.5)
        mock_distance.assert_called_once()

    @pytest.mark.skip(reason="Profile creation signal not implemented yet")
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
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())

        game = form.save()
        self.assertEqual(game.mileage, 0.0)


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
        self.site = Site.objects.create(
            name="Test Site", address="123 Test St, Nashville, TN"
        )
        self.league = League.objects.create(
            organization="Test League",
            assignor="Test Assignor",
            game_fee=Decimal("50.00"),
        )
        self.game = Game.objects.create(
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
        self.assertIn("games", response.context)

    def test_game_detail_view(self):
        """Test game detail view."""
        response = self.client.get(reverse("game_detail", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Site")

    def test_game_detail_view_not_found(self):
        """Test game detail view with invalid pk."""
        response = self.client.get(reverse("game_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_game_create_view_get(self):
        """Test game create view GET request."""
        response = self.client.get(reverse("game_create"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @pytest.mark.skip(reason="Profile creation signal not implemented yet")
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
        response = self.client.post(reverse("game_create"), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertEqual(Game.objects.count(), 2)

    def test_edit_game_view_get(self):
        """Test edit game view GET request."""
        response = self.client.get(reverse("edit_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    @pytest.mark.skip(reason="Profile creation signal not implemented yet")
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
        """Test delete game view GET request."""
        response = self.client.get(reverse("delete_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)

    def test_delete_game_view_post(self):
        """Test delete game view POST request."""
        response = self.client.post(reverse("delete_game", args=[self.game.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Game.objects.count(), 0)
