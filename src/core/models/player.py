from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Func, OuterRef, Subquery
from django.db.models.functions import Coalesce

if TYPE_CHECKING:
    from .game import Game


class PlayerQuerySet(models.QuerySet):
    def annotate_name(self):
        return self.annotate(
            player_name=Coalesce(
                "name", "user__username", output_field=models.CharField()
            )
        ).defer("name")

    def annotate_most_recent_submission(self, game: "Game"):
        from core.models.submission import Submission

        recent_sqry = Subquery(
            Submission.objects.filter(user_id=OuterRef("user__pk"), games=game)
            .order_by("datetime")
            .values("datetime")[:1]
        )
        return self.annotate(most_recent_submission=recent_sqry)

    def annotate_submission_count(self, game: "Game"):
        from core.models.game_submission import GameSubmission

        fresh_subquery = Subquery(
            GameSubmission.objects.filter(
                game=game, submission__user=OuterRef("user"), round__isnull=True
            )
            .annotate(count=Func(F("pk"), function="Count"))
            .values("count")
        )

        return self.annotate(submission_count=fresh_subquery)


class Player(models.Model):
    class Roles(models.IntegerChoices):
        PLAYER = 1
        MODERATOR = 2

    name = models.CharField(max_length=256, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    role = models.PositiveSmallIntegerField(default=Roles.PLAYER)

    objects: PlayerQuerySet = PlayerQuerySet.as_manager()

    def clean(self):
        super().clean()
        if self.user is None and self.name is None:
            raise ValidationError("both user and name cannot be null")

    def __str__(self):
        return str(self.name) if self.name else str(self.user.username)
