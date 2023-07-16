from django.conf import settings
from django.db import models


class Submission(models.Model):
    class Type(models.IntegerChoices):
        NOT_SPECIFIED = 0
        YOUTUBE = 1
        VIMEO = 2
        SPOTIFY = 3

    url = models.URLField(max_length=1024, null=True, blank=True)
    type = models.PositiveSmallIntegerField(editable=False, default=Type.NOT_SPECIFIED)
    title = models.CharField(max_length=512, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="submissions", on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(auto_now_add=True)
    games = models.ManyToManyField(
        "core.game", related_name="submissions", through="core.GameSubmission"
    )

    def __str__(self):
        return str(self.title)

    class Meta:
        pass
