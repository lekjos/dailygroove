from django.conf import settings
from django.db import models


class Player(models.Model):
    class Roles(models.IntegerChoices):
        PLAYER = 1
        MODERATOR = 2

    name = models.CharField(max_length=256, null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    role = models.PositiveSmallIntegerField(default=Roles.PLAYER)

    # @property
    # def anonymous(self):
    #     return bool(self.user)

    def __str__(self):
        return str(self.name)
