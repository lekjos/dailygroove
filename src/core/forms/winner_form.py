from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from core.models.round import Round


class WinnerForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = ["winner"]

    def __init__(self, *args, players=None, moderator_id: int = None, **kwargs):
        self.players = players
        self.moderator_id = moderator_id
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit(
                name="action",
                value="Declare Winner",
            )
        )
        self.helper.add_input(
            Submit(
                name="action",
                value="Reveal Submitter",
            )
        )

        super().__init__(*args, **kwargs)

        player_choices = [{"pk": None, "player_name": "-----"}] + list(players)
        self.fields["winner"].choices = (
            (x["pk"], x["player_name"]) for x in player_choices
        )

    def save(self, commit=True):
        self.instance.moderator_id = self.moderator_id

        super().save(self)
