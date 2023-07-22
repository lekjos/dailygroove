import logging

from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from core.models import User
from core.tokens import account_activation_token

logger = logging.getLogger(__name__)


def activate_view(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user: User = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    good_token = account_activation_token.check_token(user, token)

    if user is not None and good_token:
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect("dashboard")
    msg = f"invalid account activation detected: uidb64:{uidb64} token:{token}. user:{user}"
    logger.exception(msg)
    return render(request, "account_activation_invalid.html")


def account_activation_sent_view(request):
    return render(request, "account_activation_sent.html")
