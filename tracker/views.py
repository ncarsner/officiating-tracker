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
