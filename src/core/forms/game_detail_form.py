from django import forms

from core.forms.base_crispy_form import BaseCrispyForm
from core.models.game import Game


class GameDetailForm(BaseCrispyForm, forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "slug", "frequency", "timezone", "round_start_time"]
