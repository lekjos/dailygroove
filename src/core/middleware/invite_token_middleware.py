"""
Common business logic that's used in multiple places
"""

import logging
from typing import Optional

from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from core.models.game import Game
from core.models.player import Player
from core.utils import replace_url_params

logger = logging.getLogger(__name__)


class InviteTokenMiddleware(MiddlewareMixin):
    LOGIN_URL = reverse("login")
    EXCLUDED_URLS = [
        LOGIN_URL,
        reverse("signup"),
        reverse("account_activation_sent"),
        "/activate",  # HARDCODED, ALSO UPDATE URLS.PY
    ]

    def process_request(self, request: HttpRequest) -> Optional[HttpResponseRedirect]:
        # Check if the user is logged in
        if invite_token := request.GET.get("invite_token"):
            if request.user.is_authenticated:
                accept_game_invite(request, invite_token)
                # Remove the 'invite_token' parameter from the request
                request.GET._mutable = True  # pylint: disable=protected-access
                del request.GET["invite_token"]
                request.GET._mutable = False  # pylint: disable=protected-access
                return None

            # Check if the current URL's name is in the excluded list
            if any(str(request.path).startswith(x) for x in self.EXCLUDED_URLS):
                return None

            original_path = request.path
            return redirect(
                f"{reverse('login')}{replace_url_params(request, skip_encode_params=['next'], next=original_path)}"
            )
        return None


def accept_game_invite(request, invite_token: str):
    try:
        game = Game.objects.get(invite_token=invite_token)
    except Game.DoesNotExist:
        messages.error(request, "Invalid game invite token")
        msg = f"Invalid invite token for user: {request.user} token: {invite_token}"
        logger.exception(msg)
        return

    _, created = Player.objects.get_or_create(user=request.user, game=game)
    if created:
        messages.success(request, f"You have been added to: {game.name}!")
    else:
        messages.info(request, f"You are already a player in {game.name}!")
