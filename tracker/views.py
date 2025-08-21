from django.shortcuts import get_object_or_404, render

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
            # TODO: redirect to the game list or detail view
    context = {"form": form, "title": "Add Game"}
    return render(request, "game/add.html", context)


def edit_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    form = GameForm(instance=game)
    if request.method == "POST":
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            # TODO: redirect to the game list or detail view
    context = {"form": form, "title": "Edit Game"}
    return render(request, "game/edit.html", context)


def delete_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    if request.method == "POST":
        game.delete()
        # TODO: redirect to the game list
    context = {"game": game, "title": "Delete Game"}
    return render(request, "game/delete.html", context)
