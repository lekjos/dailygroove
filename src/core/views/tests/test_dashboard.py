import pytest

from core.models.factories import GameFactory, PlayerFactory, UserFactory
from testing_utilities.base_view_test import ViewTest


class TestDashboardAnon(ViewTest):
    URL = "dashboard"
    TEMPLATE = "dashboard.html"
    MAX_QUERIES = 7


class TestDashboardAnon(ViewTest):
    URL = "dashboard"
    TEMPLATE = "dashboard.html"
    MAX_QUERIES = 5

    @pytest.fixture
    def as_user(self):
        game = GameFactory()
        user = UserFactory()
        PlayerFactory(game=game, user=user)
        return user
