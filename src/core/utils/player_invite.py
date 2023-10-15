import logging
import socket
from smtplib import SMTPException
from typing import List

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpRequest
from django.urls import reverse

from core.models.game import Game
from core.models.user import User

logger = logging.getLogger(__name__)


def get_invite_message(game: "Game", sender: "User", is_member: bool = False):
    if is_member:
        base_url = f"{settings.ROOT_URL}{reverse('signup')}"
    else:
        base_url = settings.ROOT_URL

    return f"""You've been invited to join {sender.username}'s game on dailygroove.us: {game.name}!

Daily Groove is a music guessing game you play with friends.

To accept, click the link below and create an account if you don't have one already: 

{base_url}?invite_token={game.invite_token}

"""


def send_invite_emails(
    request: HttpRequest,
    game: "Game",
    sender: "User",
    recipient_list: List[str],
):
    def _send(recipient_list, message):
        subject = f"Invite to join {sender.username}'s game on Daily Groove"
        try:
            send_mail(
                subject=subject,
                from_email=None,
                message=message,
                recipient_list=recipient_list,
            )
        except (SMTPException, socket.error) as e:
            messages.error(
                request,
                f"There was a problem sending your message to one or more recipients: {e}",
            )
            logger.error(e)
        else:
            messages.success(request, f"Invites for {game} sent!")

    recipient_set = set(recipient_list)

    if existing_users := User.objects.filter(email__in=recipient_list).values_list(
        "email", flat=True
    ):
        _send(existing_users, get_invite_message(game, sender, is_member=True))

    if new_users := set(recipient_set).difference(existing_users):
        _send(list(new_users), get_invite_message(game, sender, is_member=False))
