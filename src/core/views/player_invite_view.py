from functools import cached_property

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import FormView

from core.forms.player_invite_form import PlayerInviteForm
from core.models.game import Game
from core.models.user import User


class PlayerInviteView(LoginRequiredMixin, FormView):
    form_class = PlayerInviteForm
    template_name = "player-invite.html"

    @cached_property
    def game(self):
        return get_object_or_404(Game, slug=self.kwargs["slug"])

    def get_invite_message(self, email=None):
        if email:
            if not User.objects.filter(email=email).exists():
                base_url = f"{settings.ROOT_URL}{reverse('signup')}"
        base_url = self.game.get_absolute_url()

        return f"""You've been invited to join {self.request.user.username}'s game on dailygroove.us: {self.game.name}!

Daily Groove is a music guessing game you play with friends.

To accept, click the link below and create an account if you don't have one already: 

<a href="{base_url}?invite_token={self.game.invite_token}">Join {self.game.name.capitalize()}</a>

"""

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context["game"] = self.game
        context["invite_message"] = self.get_invite_message()
        return context

    def get_success_url(self) -> str:
        return reverse("manage_game", kwargs={"slug": self.kwargs["slug"]})

    def form_valid(self, form):
        recipient_email = form.cleaned_data["recipient_email"]
        sender_name = self.request.user.username
        subject = f"Invite to join {sender_name}'s game on Daily Groove"
        message = self.get_invite_message(recipient_email)
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[recipient_email],
        )
        return HttpResponseRedirect(self.get_success_url())
