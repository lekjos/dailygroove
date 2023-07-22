from django import forms

from core.models.submission import Submission


class UploadFormSelectGame(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["url", "title"]


class UploadFormAllGames(forms.ModelForm):
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
        if commit:
            self.instance.save()

        super().save(self)  # pylint: disable=redundant-keyword-arg
