from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class PlayerInviteForm(forms.Form):
    recipient_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit(
                name="action",
                value="Send Invite",
            )
        )

        super().__init__(*args, **kwargs)
