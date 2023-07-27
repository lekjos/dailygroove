from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.utils.utilities import replace_url_params

from ..forms.sign_up_form import SignUpForm
from ..models import User
from ..tokens import account_activation_token


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            user.is_active = False
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
