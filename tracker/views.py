from django.shortcuts import get_object_or_404, redirect, render

from tracker.forms import GameForm
from tracker.models import Game


def game_list(request):
    """
    Handle the display and submission of the game list view.

    This view renders a list of games along with a form for adding new games.
    If the request method is POST, it processes the submitted form data, validates it,
    and saves the new game to the database if the form is valid.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML page displaying the game list and form.

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


def game_detail(request, pk):
    """
    Retrieve and display the details of a specific game.

    This view fetches a game object based on the provided primary key (pk).
    If the game does not exist, it raises a 404 error. The game details are
    then rendered in the "game/detail.html" template.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the game to retrieve.

    Returns:
        HttpResponse: The rendered HTML response displaying the game details.
    """
    game = get_object_or_404(Game, pk=pk)
    return render(request, "game/detail.html", {"game": game})


def game_create(request):
    """
    Handle the creation of a new game.

    This view renders a form for creating a new game and processes the form submission.
    If the request method is POST and the form is valid, the new game is saved to the database,
    and the user is redirected to the game list view.

    Args:
        request (HttpRequest): The HTTP request object containing metadata about the request.

    Returns:
        HttpResponse: Renders the game creation form for GET requests or invalid POST submissions.
        HttpResponseRedirect: Redirects to the game list view upon successful form submission.
    """
    form = GameForm()
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("game_list")
    context = {"form": form, "title": "Add Game"}
    return render(request, "game/add.html", context)


def edit_game(request, pk):
    """
    Handle the editing of an existing game instance.

    This view retrieves a game object by its primary key (pk) and allows
    the user to edit its details using a form. If the request method is POST,
    the form is validated and the changes are saved. If the request method
    is GET, the form is pre-filled with the game's current data.

    Args:
        request (HttpRequest): The HTTP request object containing metadata
            about the request.
        pk (int): The primary key of the game instance to be edited.

    Returns:
        HttpResponse: If the form is valid and the game is successfully updated,
            redirects to the "game_detail" view for the updated game. Otherwise,
            renders the "game/edit.html" template with the form and context.
    """
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


def delete_game(request, pk):
    """
    Handle the deletion of a specific game instance.

    This view retrieves a game object by its primary key (pk) and deletes it
    if the request method is POST. Upon successful deletion, the user is
    redirected to the game list page. If the request method is not POST,
    the view renders a confirmation page for the deletion.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the game to be deleted.

    Returns:
        HttpResponse: A redirect to the game list page upon successful deletion
        or a rendered confirmation page if the request method is not POST.

    Raises:
        Http404: If no game object with the given primary key is found.

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
