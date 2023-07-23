from django import forms

from .base_crispy_form import BaseCrispyForm


class PlayerInviteForm(BaseCrispyForm):
    recipient_email = forms.EmailField()
    SUBMIT_BUTTON_VALUE = "Send Invite"
