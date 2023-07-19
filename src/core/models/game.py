import datetime
import uuid
import zoneinfo

from django.db import models
from django.urls import reverse

from timezone_field import TimeZoneField


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
    timezone = TimeZoneField(use_pytz=False)
    round_start_time = models.TimeField(default=datetime.time(hour=10))
    invite_token = models.UUIDField(default=uuid.uuid4)

    def get_absolute_url(self):
        return reverse("game-view", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.name)
