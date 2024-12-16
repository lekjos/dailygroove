from functools import cached_property

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import BaseUpdateView
from django.views.generic.list import ListView

from core.forms.game_detail_form import GameDetailForm
from core.models import Player
from core.models.game import Game
from core.permissions import IsModeratorOrOwnerMixin
from core.utils.utilities import is_moderator


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
            Player.objects.filter(game_id=self.game.pk, disabled=False)
            .annotate_name()
            .annotate_role_name()
            .annotate_is_owner()
            .annotate_has_user()
            .values(
                "id",
                "player_name",
                "role",
                "role_name",
                "user__id",
                "has_user",
                "is_owner",
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

    def post(self, request, *args, **kwargs):
        if "player_id" in request.POST:
            action = request.POST.get("action")
            if action == "remove":
                return self.handle_player_delete(request, *args, **kwargs)
            elif action == "promote-demote":
                return self.handle_player_promote_demote(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def handle_player_delete(self, *args, **kwargs):
        if not is_moderator(self.players, self.request.user):
            raise PermissionDenied("You are not a moderator of this game.")
        player = Player.objects.get(id=self.request.POST["player_id"])
        if not player.pk in [x["id"] for x in self.players]:
            raise PermissionDenied("You cannot delete a player who isn't in your game.")
        if player.user and self.game.owner and player.user.pk == self.game.owner.pk:
            raise PermissionDenied("Cannot remove owner from game.")
        player.disabled = True
        player.save(update_fields=["disabled"])
        messages.success(
            self.request,
            f"You have successfully removed {player} from {self.game.name}",
        )
        return HttpResponseRedirect(self.get_success_url())

    def handle_player_promote_demote(self, *args, **kwargs):
        if not is_moderator(self.players, self.request.user):
            raise PermissionDenied("You are not a moderator of this game.")
        player = Player.objects.get(id=self.request.POST["player_id"])
        if not player.pk in [x["id"] for x in self.players]:
            raise PermissionDenied("You cannot delete a player who isn't in your game.")
        if player.pk == self.game.owner.pk:
            raise PermissionDenied("Cannot remove owner from game.")

        promoted = True if player.role == Player.Roles.PLAYER else False
        player.role = Player.Roles.MODERATOR if promoted else Player.Roles.PLAYER
        player.save(update_fields=["role"])
        messages.success(
            self.request,
            f'You have successfully {"promoted" if promoted else "demoted"} {player}',
        )
        return HttpResponseRedirect(self.get_success_url())
