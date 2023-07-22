# pylint: disable=cyclic-import
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    Count,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce


class PlayerQuerySet(models.QuerySet):
    def annotate_name(self):
        return self.annotate(
            player_name=Coalesce(
                "name", "user__username", output_field=models.CharField()
            )
        ).defer("name")

    def annotate_most_recent_submission(self):
        from core.models.submission import Submission

        recent_sqry = Subquery(
            Submission.objects.filter(user_id=OuterRef("user_id"))
            .order_by("datetime")
            .values("datetime")[:1]
        )
        return self.annotate(most_recent_submission=recent_sqry)

    def annotate_submission_count(self):
        return self.annotate(
            submission_count=Count(
                "user__submissions",
                filter=(
                    Q(user__submissions__rounds__isnull=True)
                    | Q(user__submissions__rounds=None)
                ),
            )
        )

    def annotate_has_user(self):
        return self.annotate(
            has_user=Case(
                When(user__isnull=False, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )


class Player(models.Model):
    class Roles(models.IntegerChoices):
        PLAYER = 1, "Player"
        MODERATOR = 2, "Moderator"

    name = models.CharField(max_length=256, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    game = models.ForeignKey("core.game", on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField(default=Roles.PLAYER)

    objects: PlayerQuerySet = PlayerQuerySet.as_manager()

    def clean(self):
        super().clean()
        if self.user is None and self.name is None:
            raise ValidationError("both user and name cannot be null")

    def __str__(self):
        if self.name:
            return self.name
        if self.user:
            return self.user.username
        return str("nameless, userless player")
