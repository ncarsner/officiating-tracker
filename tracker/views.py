from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from tracker.forms import GameForm
from tracker.models import Game


def game_list(request: HttpRequest) -> HttpResponse:
    """
    Context:
        games (QuerySet): A queryset of all games, including related league and site data.
        title (str): The title of the page, "Game List".
        form (GameForm): The form instance for adding a new game.
    """
    form = GameForm()
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
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
            return redirect("game_detail", pk=game.pk)
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
