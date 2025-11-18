from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from tracker.forms import GameForm, ProfileForm, UserForm
from tracker.models import Game, Site
from tracker.utils import distance_miles, DistanceError


@login_required
def update_profile(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ("Your profile was successfully updated!"))
            return redirect("settings:profile")
        else:
            messages.error(request, ("Please correct the error below."))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(
        request,
        "profiles/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )

def game_list(request: HttpRequest) -> HttpResponse:
    """
    Context:
        games (QuerySet): A queryset of all games, including related league and site data.
        title (str): The title of the page, "Game List".
        form (GameForm): The form instance for adding a new game.
    """
    form = GameForm(request=request)
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("game_list")
    games = Game.objects.select_related("league", "site").all()
    context = {"games": games, "title": "Game List", "form": form}
    return render(request, "game/list.html", context)


def game_detail(request: HttpRequest, pk: int) -> HttpResponse:
    game = get_object_or_404(Game, pk=pk)
    return render(request, "game/detail.html", {"game": game})


def game_create(request: HttpRequest) -> HttpResponse:
    form = GameForm()
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("game_list")
    context = {"form": form, "title": "Add Game"}
    return render(request, "game/add.html", context)


def edit_game(request: HttpRequest, pk: int) -> HttpResponse:
    game = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            return redirect("game_list")
    else:
        form = GameForm(instance=game)
    context = {"form": form, "title": "Edit Game"}
    return render(request, "game/edit.html", context)


def delete_game(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Context:
        game (Game): The game object to be deleted.
        title (str): The title for the confirmation page.
    """
    game = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        game.delete()
        return redirect("game_list")
    context = {"game": game, "title": "Delete Game"}
    return render(request, "game/delete.html", context)


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
