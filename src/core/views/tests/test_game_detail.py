import pytest

from core.models.factories import GameFactory
from test_utils.base_view_test import ViewTest


class TestGameDetailAnon(ViewTest):
    URL = "game_detail"
    EXPECTED_STATUS = 200
    TEMPLATE = "game-detail.html"
    MAX_QUERIES = 11

    @pytest.fixture(autouse=True)
    def game(self):
        return GameFactory()

    @pytest.fixture
    def url_kwargs(self, game):
        return {"slug": game.slug}


class TestReveal(TestGameDetailAnon):
    URL = "game_detail"
    METHOD = "post"
    EXPECTED_STATUS = 403
    TEMPLATE = "403.html"
    MAX_QUERIES = None
