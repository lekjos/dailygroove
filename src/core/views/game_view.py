from functools import cached_property

from django.db.models import Count, F, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from core.models.game import Game
from core.models.player import Player
from core.models.round import Round


class GameView(DetailView):
    model = Game
    template_name = "game-detail.html"
    raise_exception = True

    @cached_property
    def game(self):
        return get_object_or_404(Game, slug=self.kwargs["slug"])

    @cached_property
    def rounds(self):
        return (
            Round.objects.filter(game=self.game)
            .annotate_game()
            .order_by("-datetime")
            .values(
                "round_number",
                "datetime",
                "winner_name",
                "submitted_by",
                "title",
                "url",
            )
        )

    def get_object(self, *args, **kwargs):
        return self.game

    @property
    def next_round(self):
        return Round.objects.next_round(game=self.game)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.game.name
        context["leader_board"] = self.leader_board
        context["rounds"] = self.rounds
        next_round = self.next_round
        context["next_round"] = next_round
        return context

    @property
    def leader_board(self):
        recent_sqry = Subquery(
            Round.objects.filter(winner_id=OuterRef("pk"), game=self.game)
            .order_by("datetime")
            .values("datetime")[:1]
        )
        return (
            Player.objects.filter(game=self.game)
            .annotate(
                win_count=Count(F("wins"), filter=Q(game=self.game), distinct=True),
                most_recent_win=recent_sqry,
            )
            .order_by("-win_count")
            .values("name", "win_count", "most_recent_win")
        )
