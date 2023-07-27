from unittest import mock

from django.http import HttpResponse

import pytest

from core.forms.game_detail_form import NewGameDetailForm
from core.models.factories import UserFactory
from core.models.game import Game
from core.models.player import Player
from testing_utilities.base_view_test import ViewTest


@pytest.fixture
def test_user():
    return UserFactory()


class TestNewGameAnon(ViewTest):
    URL = "new_game"
    EXPECTED_STATUS = 200
    TEMPLATE = "registration/login.html"
    MAX_QUERIES = 3


class TestNewGameAsMod(TestNewGameAnon):
    TEMPLATE = "new-game.html"
    MAX_QUERIES = 5

    @pytest.fixture
    def as_user(self, test_user):
        return test_user

    @pytest.mark.django_db
    def test_it_returns_form(self, response):
        assert "form" in response.context
        assert response.context["form"].__class__ == NewGameDetailForm


class TestNewGamePostAnon(TestNewGameAnon):
    METHOD = "post"


class TestNewGamePostAsMod(TestNewGameAnon):
    METHOD = "post"
    TEMPLATE = "dashboard.html"
    MAX_QUERIES = 10

    @pytest.fixture
    def as_user(self, test_user):
        return test_user

    @pytest.fixture
    def request_kwargs(self):
        """passed into test client"""
        return {
            "follow": True,
            "data": {
                "name": "my new game",
                "frequency": Game.Frequency.DAILY,
                "timezone": "America/New_York",
                "round_start_time": "10:00:00",
                "emails-TOTAL_FORMS": "2",
                "emails-INITIAL_FORMS": "0",
                "emails-MIN_NUM_FORMS": "0",
                "emails-MAX_NUM_FORMS": "1000",
                "emails-0-recipient_email": "test@test.com",
                "emails-1-recipient_email": "",
                "action": "Create Game and Invite Players!",
            },
        }

    @pytest.mark.django_db
    def test_it_created_game_and_player(self, make_request, test_user):
        assert Player.objects.count() == 0
        assert Game.objects.count() == 0
        make_request()
        assert Player.objects.count() == 1
        assert Game.objects.count() == 1

        game = Game.objects.first()
        player = Player.objects.first()

        assert game.owner == test_user
        assert player.game == game
        assert player.user == test_user

    @pytest.mark.django_db
    @mock.patch("core.views.new_game_view.send_invite_emails")
    def test_it_sent_email(self, mocked_func: mock.Mock, make_request):
        make_request()
        mocked_func.assert_called_once()
