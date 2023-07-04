from django.conf import settings
from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=256, null=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def anonymous(self):
        return bool(self.user)

    def __str__(self):
        return self.name
