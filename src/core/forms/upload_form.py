from django import forms

from core.models.game import Game
from core.models.submission import Submission


class UploadFormSelectGame(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["url", "title", "games"]


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

    def save(self):
        self.instance.user = self.user
        self.instance.save()
        self.instance.games.set(
            Game.objects.filter(players__user=self.user).values_list("pk", flat=True)
        )
        print(self.instance.__dict__)
        super().save(self)
