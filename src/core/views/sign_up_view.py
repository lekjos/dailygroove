import logging

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_encode

from core.utils.utilities import replace_url_params

from ..forms.sign_up_form import SignUpForm
from ..models import User
from ..tokens import account_activation_token

logger = logging.getLogger(__name__)


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            user.is_active = False
            if (
                user.email.split("@", maxsplit=1)[-1]
                in settings.WHITELISTED_EMAIL_DOMAINS
            ):
                logger.info(
                    "A user has signed up with a whitelisted domain: %s", user.email
                )
                user.email_confirmed = True
                user.is_active = True
                user.save()
                login(request, user)
                return HttpResponseRedirect(_get_redirect_url(request))
            logger.info(
                "A user has signed up with a non-verified domain: %s", user.email
            )
            user.email_confirmed = False
            user.save()
            current_site = get_current_site(request)
            subject = "Activate Your Daily Groove"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_link = f"https://{current_site.domain}{reverse('activate', kwargs={'uidb64':uid, 'token':token})}{replace_url_params(request)}"

            message = render_to_string(
                "account-activation-email.html",
                {
                    "user": user.username,
                    "activation_link": activation_link,
                },
            )
            user.email_user(subject, message)
            return redirect("account_activation_sent")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def _get_redirect_url(request: HttpRequest):
    """Return the user-originating redirect URL if it's safe."""
    redirect_to = request.POST.get(
        REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, "")
    )
    url_is_safe = url_has_allowed_host_and_scheme(
        url=redirect_to,
        allowed_hosts=request.get_host(),
        require_https=request.is_secure(),
    )
    return redirect_to if url_is_safe else reverse("dashboard")
