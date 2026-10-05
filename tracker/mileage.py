"""Trip-based mileage aggregation.

One round trip is driven to a site on a given date, however many games are
worked there that day. Every mileage total in the application is therefore
derived from unique trips rather than from individual game rows. This module is
the single definition of that rule; callers must not sum ``Game.mileage``
directly.
"""

from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable

from tracker.models import Game


def mileage_by(
    games: Iterable[Game],
    group_key: Callable[[Game], Hashable],
) -> dict[Hashable, float]:
    """Total trip mileage per group.

    Games collapse to one trip per (date, site, group) before summing, so games
    worked at the same site on the same date contribute their mileage once. The
    trip's mileage is the largest value recorded against any of its games, which
    matches how the game list displays a trip.

    Note that a trip shared by two groups, such as two leagues played at one
    site on one date, contributes its mileage to each group. Group totals can
    therefore exceed the total returned by :func:`total_mileage`.

    Args:
        games: Games to aggregate. Access ``game.league`` or ``game.site`` in
            ``group_key`` only on a queryset that selected them, or this issues
            a query per game.
        group_key: Returns the group a game belongs to. The returned value is
            the key in the result, so it must match whatever the caller uses to
            look the total up.

    Returns:
        Mapping of group to total miles. Groups whose games all have zero
        mileage are present with a value of ``0.0``.
    """
    trips: dict[tuple[object, object, Hashable], float] = {}
    for game in games:
        trip = (game.date, game.site_id, group_key(game))
        trips[trip] = max(trips.get(trip, 0.0), game.mileage or 0.0)

    totals: dict[Hashable, float] = defaultdict(float)
    for (_, _, group), miles in trips.items():
        totals[group] += miles
    return dict(totals)


def total_mileage(games: Iterable[Game]) -> float:
    """Total trip mileage across all games, counting each trip once."""
    return sum(mileage_by(games, lambda game: None).values())
