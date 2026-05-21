from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, Count, DecimalField, F, Q, Sum, When
from django.db.models.functions import ExtractYear
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from tracker.forms import GameForm, ProfileForm, UserForm
from tracker.models import Game, Site
from tracker.utils import DistanceError, distance_miles


def home(request):
    """Landing page view."""
    return render(request, "home.html")


@login_required
def profile_view(request):
    """View user profile details."""
    return render(request, "profile/view.html", {"profile": request.user.profile})


@login_required
def profile_edit(request):
    """Edit user profile."""
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST,
            request.FILES,  # Include FILES for image upload
            instance=request.user.profile,
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile was successfully updated!")
            return redirect("profile_view")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(
        request,
        "profile/edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def game_list(request: HttpRequest) -> HttpResponse:
    form = GameForm(user=request.user)
    if request.method == "POST":
        form = GameForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("game_list")

    games = Game.objects.select_related("league", "site").filter(user=request.user)
    current_year = str(date.today().year)

    f_year = request.GET.get("filter_year", current_year)
    f_league = request.GET.get("filter_league", "")
    f_assignor = request.GET.get("filter_assignor", "")
    f_position = request.GET.get("filter_position", "")
    f_site = request.GET.get("filter_site", "")

    summary_qs = games
    if f_year:
        summary_qs = summary_qs.filter(date__year=f_year)
    if f_league:
        summary_qs = summary_qs.filter(league__organization=f_league)
    if f_assignor:
        summary_qs = summary_qs.filter(league__assignor=f_assignor)
    if f_position:
        summary_qs = summary_qs.filter(position=f_position)
    if f_site:
        summary_qs = summary_qs.filter(site__name=f_site)

    eff_fee = Case(
        When(fee__isnull=False, then=F("fee")),
        default=F("league__game_fee"),
        output_field=DecimalField(max_digits=6, decimal_places=2),
    )
    summary = summary_qs.aggregate(
        count=Count("id"),
        total_fees=Sum(eff_fee),
        paid_fees=Sum(eff_fee, filter=Q(fee_paid=True)),
        unpaid_fees=Sum(eff_fee, filter=Q(fee_paid=False, is_volunteer=False)),
        total_mileage=Sum("mileage"),
    )

    available_years = list(
        games.annotate(year=ExtractYear("date"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )
    available_leagues = list(
        games.filter(league__isnull=False)
        .values_list("league__organization", flat=True)
        .distinct()
        .order_by("league__organization")
    )
    available_assignors = list(
        games.filter(league__isnull=False)
        .values_list("league__assignor", flat=True)
        .distinct()
        .order_by("league__assignor")
    )
    available_positions = list(
        games.filter(position__isnull=False)
        .exclude(position="")
        .values_list("position", flat=True)
        .distinct()
        .order_by("position")
    )
    available_sites = list(
        games.filter(site__isnull=False)
        .values_list("site__name", flat=True)
        .distinct()
        .order_by("site__name")
    )

    context = {
        "games": games,
        "title": "Game List",
        "form": form,
        "summary": summary,
        "current_year": current_year,
        "f_year": f_year,
        "f_league": f_league,
        "f_assignor": f_assignor,
        "f_position": f_position,
        "f_site": f_site,
        "available_years": available_years,
        "available_leagues": available_leagues,
        "available_assignors": available_assignors,
        "available_positions": available_positions,
        "available_sites": available_sites,
    }
    return render(request, "game/list.html", context)


@login_required
def game_detail(request: HttpRequest, pk: int) -> HttpResponse:
    game = get_object_or_404(Game, pk=pk, user=request.user)
    return render(request, "game/detail.html", {"game": game})


@login_required
def game_create(request: HttpRequest) -> HttpResponse:
    form = GameForm(user=request.user)
    if request.method == "POST":
        form = GameForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("game_list")
    context = {"form": form, "title": "Add Game"}
    return render(request, "game/add.html", context)


@login_required
def edit_game(request: HttpRequest, pk: int) -> HttpResponse:
    game = get_object_or_404(Game, pk=pk, user=request.user)
    if request.method == "POST":
        form = GameForm(request.POST, instance=game, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("game_list")
    else:
        form = GameForm(instance=game, user=request.user)
    context = {"form": form, "title": "Edit Game"}
    return render(request, "game/edit.html", context)


@login_required
def delete_game(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Context:
        game (Game): The game object to be deleted.
        title (str): The title for the confirmation page.
    """
    game = get_object_or_404(Game, pk=pk, user=request.user)
    if request.method == "POST":
        game.delete()
        return redirect("game_list")
    context = {"game": game, "title": "Delete Game"}
    return render(request, "game/delete.html", context)


@login_required
def game_stats(request: HttpRequest) -> HttpResponse:
    base_qs = Game.objects.filter(user=request.user)
    eff_fee = Case(
        When(fee__isnull=False, then=F("fee")),
        default=F("league__game_fee"),
        output_field=DecimalField(max_digits=6, decimal_places=2),
    )
    stat_annotations = dict(
        count=Count("id"),
        total_fees=Sum(eff_fee),
        paid_fees=Sum(eff_fee, filter=Q(fee_paid=True)),
        unpaid_fees=Sum(eff_fee, filter=Q(fee_paid=False, is_volunteer=False)),
        total_mileage=Sum("mileage"),
    )
    by_year = (
        base_qs.annotate(year=ExtractYear("date"))
        .values("year")
        .annotate(**stat_annotations)
        .order_by("-year")
    )
    by_league = (
        base_qs.values("league__organization")
        .annotate(**stat_annotations)
        .order_by("league__organization")
    )
    by_assignor = (
        base_qs.values("league__assignor")
        .annotate(**stat_annotations)
        .order_by("league__assignor")
    )
    by_position = (
        base_qs.values("position").annotate(**stat_annotations).order_by("position")
    )
    by_site = (
        base_qs.values("site__name").annotate(**stat_annotations).order_by("site__name")
    )
    context = {
        "title": "Stats",
        "by_year": by_year,
        "by_league": by_league,
        "by_assignor": by_assignor,
        "by_position": by_position,
        "by_site": by_site,
    }
    return render(request, "game/stats.html", context)


@login_required
def site_distance(request):
    site_id = request.GET.get("site")
    miles = 0
    if site_id and request.user.profile.location:
        try:
            site = Site.objects.get(pk=site_id)
            miles = distance_miles(request.user.profile.location, site.address)
        except DistanceError:
            miles = 0

    form = GameForm()  # empty form just for rendering the field
    form.fields["mileage"].initial = miles
    html = render_to_string("game/_mileage_field.html", {"form": form}, request)
    return HttpResponse(html)
