from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView

from core.models import Player
from core.models.game import Game


class ManageGameView(ListView):
    model = Player
    template_name = "manage-game.html"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        ctx["game"] = get_object_or_404(Game, slug=self.kwargs["slug"])
        return ctx

    def get_queryset(self):
        game_slug = self.kwargs["slug"]
        return (
            Player.objects.filter(game_id=game_slug)
            .annotate_name()
            .annotate_has_user()
            .values(
                "pk",
                "player_name",
                "has_user",
            )
        )
