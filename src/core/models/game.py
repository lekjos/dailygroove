from django.db import models
from django.urls import reverse


class Game(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(primary_key=True)
    players = models.ManyToManyField("core.player")
    owner = models.ForeignKey(
        "core.player", related_name="owned_games", on_delete=models.CASCADE
    )

    def get_absolute_url(self):
        return reverse("game-view", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.name)
