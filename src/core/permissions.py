from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured

from core.utils import is_moderator


class IsModeratorOrOwnerMixin(UserPassesTestMixin):
    def test_func(self):
        if not hasattr(self, "players"):
            raise ImproperlyConfigured(
                "To use IsModeratorOrOwnerMixin, must define players property as .values with 'role' and 'user__id' annotated"
            )

        return is_moderator(self.players, self.request.user)
