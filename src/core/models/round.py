from django.db import models


class Round(models.Model):
    winner = models.ForeignKey(
        "core.player",
        related_name="wins",
        on_delete=models.CASCADE,
    )
    submitter = models.ForeignKey(
        "core.player",
        related_name="submissions",
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
