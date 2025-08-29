from django.shortcuts import get_object_or_404, redirect, render

from tracker.forms import GameForm
from tracker.models import Game


# Create your views here.
def game_list(request):
    form = GameForm()
    # TODO: handle successful form submission (e.g., redirect)
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
    # TODO: reload objects after db insert
    games = Game.objects.select_related("league", "site").all()
    context = {"games": games, "title": "Game List", "form": form}
    return render(request, "game/list.html", context)


def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    return render(request, "game/detail.html", {"game": game})


def game_create(request):
    form = GameForm()
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("game_list")  # Redirect to the game list view
    context = {"form": form, "title": "Add Game"}
    return render(request, "game/add.html", context)


def edit_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    form = GameForm(instance=game)  # Provide the instance to pre-fill the form
    if request.method == "POST":
        form = GameForm(request.POST, instance=game)  # Bind the form to the instance
        if form.is_valid():
            form.save()
            return redirect(
                "game_detail", pk=game.pk
            )  # Redirect to the game detail view
    context = {"form": form, "title": "Edit Game"}
    return render(request, "game/edit.html", context)


def delete_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        game.delete()
        return redirect(
            "game_list"
        )  # Redirect to the game list upon successful deletion
    context = {"game": game, "title": "Delete Game"}
    return render(request, "game/delete.html", context)
