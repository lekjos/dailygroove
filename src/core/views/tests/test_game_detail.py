import random

import factory
import pytest

from core.models.factories import (
    GameFactory,
    PlayerFactory,
    SubmissionFactory,
    UserFactory,
)
from core.models.player import Player
from test_utils.base_view_test import ViewTest


@pytest.fixture
def moderator():
    return UserFactory()


class TestGameDetailAnon(ViewTest):
    URL = "game_detail"
    EXPECTED_STATUS = 200
    TEMPLATE = "game-detail.html"
    MAX_QUERIES = 11

    @pytest.fixture(autouse=True)
    def game(self, moderator):
        game = GameFactory()
        PlayerFactory(user=moderator, game=game, role=Player.Roles.MODERATOR)
        players = PlayerFactory.create_batch(5, game=game, role=Player.Roles.PLAYER)
        users = [x.user for x in players]
        submission_ct = 15
        SubmissionFactory.create_batch(
            submission_ct,
            user=factory.Iterator([random.choice(users) for _ in range(submission_ct)]),
        )
        return game

    @pytest.fixture
    def url_kwargs(self, game):
        return {"slug": game.slug}


class TestRevealAnon(TestGameDetailAnon):
    URL = "game_detail"
    METHOD = "post"
    EXPECTED_STATUS = 403
    TEMPLATE = "403.html"
    MAX_QUERIES = None


class TestRevealAsMod(TestGameDetailAnon):
    METHOD = "post"
    EXPECTED_STATUS = 200
    MAX_QUERIES = 16

    @pytest.fixture
    def as_user(self, moderator):
        return moderator

    @pytest.fixture
    def request_kwargs(self):
        """passed into test client"""
        return {
            "data": {
                "action": "Reveal Submitter",
            },
        }

    @pytest.mark.django_db
    def test_winner_in_context(self, response):
        assert "submitted_by" in response.context
