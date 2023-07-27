import logging
from functools import cached_property

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import FormView

from core.forms.player_invite_form import PlayerInviteForm
from core.models.game import Game
from core.utils.player_invite import get_invite_message, send_invite_emails

logger = logging.getLogger(__name__)


class PlayerInviteView(LoginRequiredMixin, FormView):
    form_class = PlayerInviteForm
    template_name = "player-invite.html"

    @cached_property
    def game(self):
        return get_object_or_404(Game, slug=self.kwargs["slug"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["invite_message"] = get_invite_message(self.game, self.request.user)
        return context

    def get_success_url(self) -> str:
        return reverse("manage_game", kwargs={"slug": self.kwargs["slug"]})

    def form_valid(self, form):
        recipient_email = form.cleaned_data["recipient_email"]
        send_invite_emails(
            self.request,
            game=self.game,
            sender=self.request.user,
            recipient_list=[recipient_email],
        )

        return HttpResponseRedirect(self.get_success_url())
