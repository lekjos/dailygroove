from django import forms

from core.forms.base_crispy_form import BaseCrispyForm
from core.models.submission import Submission


class UploadFormAllGames(BaseCrispyForm, forms.ModelForm):
    SUBMIT_BUTTON_VALUE = "Submit Groove"

    class Meta:
        model = Submission
        fields = [
            "url",
            "title",
        ]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.user = self.user

        super().save()
