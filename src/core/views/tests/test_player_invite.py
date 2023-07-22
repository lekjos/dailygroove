from django.urls import reverse

import pytest

from core.models.factories import GameFactory, PlayerFactory, UserFactory
from core.models.player import Player
from test_utils.base_view_test import ViewTest


@pytest.fixture
def moderator(game):
    user = UserFactory()
    PlayerFactory(user=user, game=game, role=Player.Roles.MODERATOR)
    return user


class InvitePlayerTestBase:
    MAX_QUERIES = 11
    URL = "player_invite"
    TEMPLATE = "player-invite.html"

    @pytest.fixture(autouse=True)
    def game(self):
        return GameFactory()

    @pytest.fixture(autouse=True)
    def url_kwargs(self, game):
        return {"slug": game.slug}


class TestPlayerInvite:
    class CaseAsAnonGet(InvitePlayerTestBase, ViewTest):
        EXPECTED_STATUS = 200
        TEMPLATE = "registration/login.html"

    class CaseAsAnonPost(InvitePlayerTestBase, ViewTest):
        EXPECTED_STATUS = 200
        METHOD = "post"
        TEMPLATE = "registration/login.html"

    class ContextAsModerator:
        class CaseGet(InvitePlayerTestBase, ViewTest):
            EXPECTED_STATUS = 200

            @pytest.fixture
            def as_user(self, moderator):
                return moderator

        class CasePostInvalid(InvitePlayerTestBase, ViewTest):
            EXPECTED_STATUS = 200
            METHOD = "post"

            @pytest.fixture
            def as_user(self, moderator):
                return moderator

        class CasePostValid(InvitePlayerTestBase, ViewTest):
            EXPECTED_STATUS = 200
            METHOD = "post"
            TEMPLATE = "manage-game.html"

            @pytest.fixture
            def as_user(self, moderator):
                return moderator

            @pytest.fixture
            def request_kwargs(self):
                """passed into test client"""
                return {"follow": True, "data": {"recipient_email": "test@test.com"}}
