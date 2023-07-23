from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Union

from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce

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

    def current_round(self, game: Union["Game", int]):
        from core.models.game import Game

        game_tz = game.timezone
        frequency = game.frequency
        now: datetime = datetime.now(game_tz)

        def _get_date_range():
            match frequency:
                case Game.Frequency.MANUAL:
                    start_date = end_date = now + timedelta(days=10)
                case Game.Frequency.DAILY:
                    start_date = now
                    end_date = now
                case Game.Frequency.WEEKDAYS:
                    start_date = now
                    while start_date.weekday() >= 5:  # Saturday is 5, Sunday is 6
                        start_date -= timedelta(days=1)

                    end_date = start_date
                    if start_date.weekday() >= 5:
                        end_date = start_date + timedelta(days=6 - start_date.weekday())

                case Game.Frequency.WEEKLY:
                    start_date = now
                    while start_date.weekday() > 0:
                        start_date -= timedelta(days=1)
                    end_date = start_date + timedelta(days=6)

            return (
                start_date.replace(hour=0, minute=0, second=0, microsecond=0),
                end_date.replace(hour=23, minute=59, second=59),
            )

        game_id = game.pk if isinstance(game, Game) else game
        start_date, end_date = _get_date_range()

        most_recent_round = Round.objects.filter(
            game_id=game_id,
            datetime__gte=start_date,
            datetime__lt=end_date,
        ).order_by("-round_number")

        if not most_recent_round:
            most_recent_round = Round.objects.create(game_id=game_id)
        else:
            most_recent_round = most_recent_round.first()

        if now < end_date:
            most_recent_round.next_round_at = end_date
        else:
            most_recent_round.round_ends_at = end_date

        return most_recent_round


class Round(models.Model):
    winner = models.ForeignKey(
        "core.player",
        related_name="wins",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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

    def shuffle(self):
        self.submission_id = Submission.objects.get_fresh_groove_pk()
        self.save()

    def save(self, *args, **kwargs):
        self._set_default_round_number()
        self._set_default_submission()

        super().save()

    def _set_default_round_number(self):
        if not self.round_number:
            top_round_number = (
                Round.objects.filter(game=self.game)
                .order_by("-round_number")
                .values_list("round_number", flat=True)
                .first()
            ) or 0

            self.round_number = top_round_number + 1

    def _set_default_submission(self):
        from ..models.submission import Submission

        try:
            self.submission
        except Submission.DoesNotExist:
            self.submission_id = Submission.objects.get_fresh_groove_pk()

    def __str__(self):
        return f"{self.game} - round {self.round_number}"
