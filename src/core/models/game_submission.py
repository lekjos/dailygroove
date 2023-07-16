from django.db import models


class GameSubmission(models.Model):
    game = models.ForeignKey("core.Game", on_delete=models.CASCADE)
    submission = models.ForeignKey("core.Submission", on_delete=models.CASCADE)
    round = models.ForeignKey(
        "core.Round", null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.game.name} - {self.submission.title}"
