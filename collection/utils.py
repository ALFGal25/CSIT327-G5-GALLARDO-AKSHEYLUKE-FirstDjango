from django.db.models import Sum

from .models import Game, WantedGame


def collection_summary(user):
    """Numbers shown on the dashboard and profile page."""
    games = Game.objects.filter(owner=user)
    total = games.aggregate(total=Sum("price"))["total"] or 0
    return {
        "owned_count": games.count(),
        "wanted_count": WantedGame.objects.filter(owner=user).count(),
        "total_value": total,
    }
