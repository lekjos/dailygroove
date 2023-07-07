from django.db import models


class Submission(models.Model):
    class Type(models.IntegerChoices):
        NOT_SPECIFIED = 0
        YOUTUBE = 1
        VIMEO = 2
        SPOTIFY = 3

    url = models.URLField(max_length=1024, null=True, blank=True)
    type = models.PositiveSmallIntegerField(editable=False, null=True, blank=True)
    title = models.CharField(max_length=512, default=Type.NOT_SPECIFIED)
    description = models.TextField(max_length=512, null=True, blank=True)
    player = models.ManyToManyField("core.player", related_name="submissions")
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        pass
