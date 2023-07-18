import datetime
import zoneinfo

from django.db import models
from django.urls import reverse


def get_timezone_choices():
    return ((x, x) for x in zoneinfo.available_timezones())


class Game(models.Model):
    class Frequency(models.IntegerChoices):
        MANUAL = 0
        DAILY = 1
        WEEKDAYS = 2
        WEEKLY = 3
        MONTHLY = 4

    name = models.CharField(max_length=256)
    slug = models.SlugField(primary_key=True)
    players = models.ManyToManyField("core.player")
    owner = models.ForeignKey(
        "core.player", related_name="owned_games", on_delete=models.CASCADE
    )
    frequency = models.PositiveSmallIntegerField(
        choices=Frequency.choices, default=Frequency.WEEKDAYS
    )
    timezone = models.CharField(
        choices=get_timezone_choices(), max_length=32, default="America/Los_Angeles"
    )
    round_start_time = models.TimeField(default=datetime.time(hour=10))

    def get_absolute_url(self):
        return reverse("game-view", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.name)
