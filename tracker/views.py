from django.shortcuts import render, get_object_or_404
from tracker.models import Game, League, Site
from tracker.forms import GameForm


# Create your views here.
def game_list(request):
    context = {}
    form = GameForm()
    games = Game.objects.select_related('league', 'site').all()
    context['games'] = games
    context['title'] = 'Game List'
    context['form'] = form
    return render(request, 'game/list.html', context)

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    return render(request, 'game/detail.html', {'game': game})