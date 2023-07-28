# pylint: disable=cyclic-import

from django.conf import settings
from django.db import models
from django.db.models import Exists, OuterRef

import pandas as pd

from core.exceptions import NoEligibleSubmissionsError


class SubmissionQuerySet(models.QuerySet):
    def annotate_fresh(self):
        from core.models.round import Round

        return self.annotate(fresh=~Exists(Round.objects.filter(pk=OuterRef("pk"))))

    def get_fresh_groove_pk(self, game_id: int) -> int:
        """
        Returns the pk of a fresh groove for the selected game.

        Raises NoEligibleSubmissionsError if there are no submissions left

        """
        cols = ("pk", "user_id")
        all_eligible = Submission.objects.filter(
            round__isnull=True, user__player__game__pk=game_id
        ).values_list(*cols)

        if all_eligible:
            df = pd.DataFrame(all_eligible)
            df = df.rename(columns=dict(enumerate(cols)))

            random_submissions = (
                df.groupby("user_id")["pk"]
                .apply(lambda x: x.sample(n=1))
                .reset_index(drop=True)
            )
            return random_submissions.sample(n=1).values[0]
        raise NoEligibleSubmissionsError()


class Submission(models.Model):
    class Type(models.IntegerChoices):
        NOT_SPECIFIED = 0
        YOUTUBE = 1
        VIMEO = 2
        SPOTIFY = 3

    url = models.URLField(max_length=1024, null=True, blank=True)
    type = models.PositiveSmallIntegerField(editable=False, default=Type.NOT_SPECIFIED)
    title = models.CharField(max_length=512, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="submissions", on_delete=models.CASCADE
    )
    datetime = models.DateTimeField(auto_now_add=True)

    objects: SubmissionQuerySet = SubmissionQuerySet.as_manager()

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        pass
