from django.db import models
from django.db.models import F


class RoundQuerySet(models.QuerySet):
    def annotate_winner_name(self):
        return self.annotate(winner_name=F("winner__name"))

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
        top_round_number = (
            Round.objects.filter(game=self.game)
            .order_by("-round_number")
            .values_list("round_number", flat=True)
            .first()
        ) or 0

        self.round_number = top_round_number + 1

        super().save(*args, *kwargs)

    def __str__(self):
        return f"{self.game} - round {self.round_number}"
