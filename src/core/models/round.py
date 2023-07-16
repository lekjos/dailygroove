import zoneinfo
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Union

from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce

import pandas as pd

if TYPE_CHECKING:
    from core.models.game import Game


class RoundQuerySet(models.QuerySet):
    def annotate_winner_name(self):
        return self.annotate(
            winner_name=Coalesce("winner__name", "winner__user__username")
        )

    def annotate_game(self):
        """
        - winner_name
        - submitted_by (user_name)
        - title
        - url
        """
        return self.annotate_winner_name().annotate(
            submitted_by=F("submission__user__username"),
            title=F("submission__title"),
            url=F("submission__url"),
        )

    def next_round(self, game: Union["Game", int]):
        from core.models.game import Game

        game_tz = zoneinfo.ZoneInfo(game.timezone)
        frequency = game.frequency
        now: datetime = datetime.now(game_tz)

        def _get_start_date():
            match frequency:
                case Game.Frequency.MANUAL:
                    pass
                case Game.Frequency.DAILY:
                    start_date = now
                case Game.Frequency.WEEKDAYS:
                    start_date = now - timedelta(days=now.weekday())
                case Game.Frequency.WEEKLY:
                    start_date = now
                    while start_date.weekday() >= 5:  # Saturday is 5, Sunday is 6
                        start_date -= timedelta(days=1)

            return start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if isinstance(game, Game):
            game = game.pk
        start_date = _get_start_date()

        most_recent_round = Round.objects.filter(
            game_id=game, datetime__gte=start_date, datetime__lt=now
        ).order_by("-round_number")

        if not most_recent_round:
            return Round.objects.create(game=game)
        else:
            return most_recent_round.first()


class Round(models.Model):
    winner = models.ForeignKey(
        "core.player",
        related_name="wins",
        on_delete=models.CASCADE,
    )
    submission = models.ForeignKey(
        "core.submission",
        related_name="rounds",
        on_delete=models.CASCADE,
    )
    moderator = models.ForeignKey(
        "core.player",
        related_name="moderated_rounds",
        on_delete=models.CASCADE,
        help_text="what user recorded the winner",
        null=True,
        blank=True,
    )
    game = models.ForeignKey("core.game", on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField(editable=False, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)

    objects: RoundQuerySet = RoundQuerySet.as_manager()

    class Meta:
        unique_together = ("round_number", "game")

    def save(self, *args, **kwargs):
        from ..models.game_submission import GameSubmission

        self._set_default_round_number()
        self._set_default_submission()

        super().save(*args, *kwargs)
        GameSubmission.objects.filter(
            submission_id=self.submission.pk, game_id=self.game.pk
        ).update(round_id=self.pk)

    def _set_default_round_number(self):
        top_round_number = (
            Round.objects.filter(game=self.game)
            .order_by("-round_number")
            .values_list("round_number", flat=True)
            .first()
        ) or 0

        self.round_number = top_round_number + 1

    def _set_default_submission(self):
        from ..models.submission import Submission

        if not self.submission:
            cols = ("pk", "user_id")
            all_eligible = Submission.objects.filter(
                games=self, gamesubmission__round__isnull=True
            ).values_list(*cols)

            df = pd.DataFrame(all_eligible)
            df = df.rename(columns=dict(enumerate(cols)))

            random_submissions = (
                df.groupby("user_id")["pk"]
                .apply(lambda x: x.sample(n=1))
                .reset_index(drop=True)
            )
            self.submission = random_submissions.sample(n=1)["pk"].values[0]

    def __str__(self):
        return f"{self.game} - round {self.round_number}"
