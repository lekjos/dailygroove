from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.forms.base_crispy_form import BaseCrispyForm
from core.models import User


class SignUpForm(BaseCrispyForm, UserCreationForm):
    SUBMIT_BUTTON_VALUE = "Sign up"
    email = forms.EmailField(
        max_length=254, help_text="A valid email address is required."
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )
