from django import forms

from crispy_forms.layout import Submit

from core.forms.base_crispy_form import BaseCrispyForm
from core.models.round import Round


class WinnerForm(BaseCrispyForm, forms.ModelForm):
    SUBMIT_BUTTON_VALUE = "Declare Winner"
    SUBMIT_BUTTON_CSS_CLASSES = "btn-no-bg btn-outline-info"

    class Meta:
        model = Round
        fields = ["winner"]

    def __init__(
        self,
        *args,
        players=None,
        enable_reroll=True,
        moderator_id: int = None,
        **kwargs
    ):
        self.moderator_id = moderator_id
        super().__init__(*args, **kwargs)

        if self.instance.winner:
            self.helper.inputs.clear()
            self.helper.add_input(
                Submit(
                    name="action",
                    value="Start Next Round",
                    css_class="btn-no-bg btn-outline-primary",
                )
            )
            del self.fields["winner"]
        else:
            self.players = players

            player_choices = [{"pk": None, "player_name": "-----"}] + list(players)
            self.fields["winner"].choices = (
                (x["pk"], x["player_name"]) for x in player_choices
            )

            self.helper.add_input(
                Submit(
                    name="action",
                    value="Reveal Submitter",
                    css_class="btn-no-bg btn-outline-danger",
                )
            )
            if enable_reroll:
                self.helper.add_input(
                    Submit(
                        name="action",
                        value="Shuffle",
                        css_class="btn-no-bg btn-outline-primary",
                    )
                )

    def save(self, commit=True):
        self.instance.moderator_id = self.moderator_id

        super().save(self)
