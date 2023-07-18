from django import forms

from core.models.round import Round


class WinnerForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = ["winner"]

    def __init__(self, *args, players=None, moderator_id: int = None, **kwargs):
        self.players = players
        self.moderator_id = moderator_id
        super().__init__(*args, **kwargs)

        self.fields["winner"].choices = ((x["pk"], x["player_name"]) for x in players)

    def save(self, commit=True):
        self.instance.moderator_id = self.moderator_id

        super().save(self)
