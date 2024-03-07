from django import forms

from core.forms.base_crispy_form import BaseCrispyForm
from core.models.game import Game


class NewGameDetailForm(BaseCrispyForm, forms.ModelForm):
    SUBMIT_BUTTON_VALUE = None

    def extra_init(self):
        self.helper.form_tag = False

    class Meta:
        model = Game
        fields = ["name", "frequency", "timezone", "round_start_time"]


class GameDetailForm(BaseCrispyForm, forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "slug", "frequency", "timezone", "round_start_time"]
