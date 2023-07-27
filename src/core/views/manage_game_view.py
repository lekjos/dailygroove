from functools import cached_property

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import BaseUpdateView
from django.views.generic.list import ListView

from core.forms.game_detail_form import GameDetailForm
from core.models import Player
from core.models.game import Game
from core.permissions import IsModeratorOrOwnerMixin


class ManageGameView(IsModeratorOrOwnerMixin, BaseUpdateView, ListView):
    model = Player
    template_name = "manage-game.html"
    form_class = GameDetailForm

    def get_success_url(self) -> str:
        return reverse("manage_game", kwargs={"slug": self.game.slug})

    @cached_property
    def game(self):
        return get_object_or_404(Game, slug=self.kwargs["slug"])

    @cached_property
    def players(self):
        return (
            Player.objects.filter(game_id=self.game.pk)
            .annotate_name()
            .annotate_has_user()
            .values(
                "pk",
                "player_name",
                "role",
                "user__id",
                "has_user",
            )
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        ctx["game"] = self.game
        return ctx

    def get_queryset(self):
        return self.players

    def get_object(self, queryset=None):
        return self.game
