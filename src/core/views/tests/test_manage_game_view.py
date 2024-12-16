import random

import factory
import pytest

from core.forms.game_detail_form import GameDetailForm
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
def moderator_user():
    return UserFactory()


class TestManageGameAnon(ViewTest):
    URL = "manage_game"
    EXPECTED_STATUS = 200
    TEMPLATE = "registration/login.html"
    MAX_QUERIES = 4

    @pytest.fixture(autouse=True)
    def game(self, moderator_user):
        game = GameFactory()
        return game

    @pytest.fixture(autouse=True)
    def players(self, game):
        players = PlayerFactory.create_batch(10, game=game, role=Player.Roles.PLAYER)
        users = [x.user for x in players]
        submission_ct = 25
        SubmissionFactory.create_batch(
            submission_ct,
            user=factory.Iterator([random.choice(users) for _ in range(submission_ct)]),
        )
        return players

    @pytest.fixture(autouse=True)
    def moderator_player(self, game, moderator_user):
        return PlayerFactory(
            game=game, user=moderator_user, role=Player.Roles.MODERATOR
        )

    @pytest.fixture(autouse=True)
    def initial_round(self, game, players):
        return RoundFactory(game=game, winner=None)

    @pytest.fixture
    def url_kwargs(self, game):
        return {"slug": game.slug}


class TestManageGameAsMod(TestManageGameAnon):
    TEMPLATE = "manage-game.html"
    MAX_QUERIES = 5

    @pytest.fixture
    def as_user(self, moderator_user):
        return moderator_user

    @pytest.mark.django_db
    def test_it_returns_form(self, response, game):
        assert "form" in response.context
        assert response.context["form"].__class__ == GameDetailForm


class TestManageGameDeletePlayerNoAuth(TestManageGameAnon):
    EXPECTED_STATUS = 403
    MAX_QUERIES = 11
    METHOD = "post"
    TEMPLATE = None

    @pytest.fixture
    def as_user(self):
        return UserFactory()

    @pytest.fixture
    def request_kwargs(self, players):
        """passed into test client"""
        return {
            "follow": True,
            "data": {"player_id": f"{players[0].pk}", "action": "remove"},
        }


class TestManageGameDeletePlayer(TestManageGameAnon):
    EXPECTED_STATUS = 200
    MAX_QUERIES = 13
    METHOD = "post"
    TEMPLATE = "manage-game.html"

    @pytest.fixture
    def as_user(self, moderator_user):
        return moderator_user

    @pytest.fixture
    def player_to_delete_pk(self, players):
        return players[0].pk

    @pytest.fixture
    def request_kwargs(self, players, game, player_to_delete_pk):
        """passed into test client"""
        return {
            "follow": True,
            "data": {"player_id": f"{player_to_delete_pk}", "action": "remove"},
        }

    @pytest.mark.django_db
    def test_it_deleted_player(self, response, player_to_delete_pk):
        p = Player.objects.get(id=player_to_delete_pk)
        assert p.disabled == True
