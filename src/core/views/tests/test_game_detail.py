import random

import factory
import pytest

from core.models.factories import (
    GameFactory,
    PlayerFactory,
    RoundFactory,
    SubmissionFactory,
    UserFactory,
)
from core.models.player import Player
from testing_utilities.base_view_test import ViewTest


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
        players = PlayerFactory.create_batch(10, game=game, role=Player.Roles.PLAYER)
        users = [x.user for x in players]
        submission_ct = 25
        SubmissionFactory.create_batch(
            submission_ct,
            user=factory.Iterator([random.choice(users) for _ in range(submission_ct)]),
        )
        return game

    @pytest.fixture(autouse=True)
    def initial_round(self, game):
        return RoundFactory(game=game, winner=None)

    @pytest.fixture
    def url_kwargs(self, game):
        return {"slug": game.slug}


class TestRevealAnon(TestGameDetailAnon):
    URL = "game_detail"
    METHOD = "post"
    EXPECTED_STATUS = 403
    TEMPLATE = "403.html"
    MAX_QUERIES = None


class PostAsMod:
    METHOD = "post"
    EXPECTED_STATUS = 200

    @pytest.fixture
    def as_user(self, moderator):
        return moderator


class TestRevealAsMod(PostAsMod, TestGameDetailAnon):
    MAX_QUERIES = 14

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


class TestDeclareWinnerAsMod(PostAsMod, TestGameDetailAnon):
    MAX_QUERIES = 21

    @pytest.fixture
    def winner(self, game):
        return Player.objects.filter(game=game).order_by("pk").first()

    @pytest.fixture
    def request_kwargs(self, winner):
        """passed into test client"""
        return {
            "follow": True,
            "data": {"action": "Declare Winner", "winner": winner.pk},
        }

    @pytest.mark.django_db
    def test_winner_in_context(self, make_request, initial_round, winner):
        assert initial_round.winner is None
        response = make_request()
        assert response.context["current_round"].pk == initial_round.pk
        actual = response.context["current_round"].winner
        expected = winner
        assert actual == expected


class TestShuffleAsMod(PostAsMod, TestGameDetailAnon):
    MAX_QUERIES = 14

    @pytest.fixture
    def request_kwargs(self):
        """passed into test client"""
        return {
            "follow": True,
            "data": {"action": "Shuffle"},
        }

    @pytest.mark.django_db
    def test_new_submission_in_context(self, make_request, initial_round):
        response = make_request()
        assert (
            initial_round.submission.pk
            != response.context["current_round"].submission.pk
        )
