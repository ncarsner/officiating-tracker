from django.shortcuts import render, get_object_or_404
from tracker.models import Game, League, Site


# Create your views here.
def game_list(request):
    games = Game.objects.all()
    return render(request, 'game/list.html', {'games': games})

def game_detail(request, pk):
    # game = Game.objects.get(pk=pk)
    game = get_object_or_404(Game, pk=pk)
    return render(request, 'game/detail.html', {'game': game})