import pytest

from core.models.factories import GameFactory, PlayerFactory, UserFactory
from test_utils.base_view_test import ViewTest


class TestDashboardAnon(ViewTest):
    URL = "dashboard"
    TEMPLATE = "dashboard.html"


class TestDashboardAnon(ViewTest):
    URL = "dashboard"
    TEMPLATE = "dashboard.html"

    @pytest.fixture
    def as_user(self):
        game = GameFactory()
        user = UserFactory()
        PlayerFactory(game=game, user=user)
        return user
