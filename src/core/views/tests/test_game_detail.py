import pytest

from core.models.factories import GameFactory
from test_utils.base_view_test import ViewTest


class TestActivateValid(ViewTest):
    URL = "game_detail"
    EXPECTED_STATUS = 200
    TEMPLATE = "game-detail.html"

    @pytest.fixture(autouse=True)
    def game(self):
        return GameFactory()

    @pytest.fixture
    def url_kwargs(self, game):
        return {"slug": game.slug}
