from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    """
    Context:
        games (QuerySet): A queryset of all games, including related league and site data.
        title (str): The title of the page, "Game List".
        form (GameForm): The form instance for adding a new game.
    """
    form = GameForm(user=request.user)
    if request.method == "POST":
        form = GameForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("game_list")
    games = Game.objects.select_related("league", "site").all()
    context = {"games": games, "title": "Game List", "form": form}
    return render(request, "game/list.html", context)


@login_required
def game_detail(request: HttpRequest, pk: int) -> HttpResponse:
    game = get_object_or_404(Game, pk=pk)
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
    game = get_object_or_404(Game, pk=pk)
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
