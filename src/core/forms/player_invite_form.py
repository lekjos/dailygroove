from django import forms

from .base_crispy_form import BaseCrispyForm


class PlayerInviteForm(BaseCrispyForm):
    recipient_email = forms.EmailField()
    SUBMIT_BUTTON_VALUE = "Send Invite"


class MultiPlayerInviteForm(BaseCrispyForm):
    recipient_email = forms.EmailField(label="")
    SUBMIT_BUTTON_VALUE = None

    def extra_init(self):
        self.helper.form_tag = False


EmailFormSet = forms.formset_factory(MultiPlayerInviteForm, extra=7)
