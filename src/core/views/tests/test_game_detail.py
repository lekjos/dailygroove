from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import pytest

from core.models.factories import GameFactory
from core.tokens import account_activation_token
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
