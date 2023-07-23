from django.core.exceptions import ValidationError

import pytest

from core.models.factories import PlayerFactory, UserFactory
from core.models.player import Player


@pytest.fixture
def no_user_player():
    return PlayerFactory(name="bob", user=None)


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def user_player(user):
    return PlayerFactory(name=None, user=user)


class TestPlayerString:
    @pytest.mark.django_db
    def test_no_user(self, no_user_player):
        assert str(no_user_player) == no_user_player.name

    def test_no_user_no_name(self):
        p = Player()
        assert str(p) == "nameless, userless player"

    @pytest.mark.django_db
    def test_str_with_user(self, user_player):
        assert str(user_player) == user_player.user.username

    @pytest.mark.django_db
    def test_str_cant_create_orphan(self):
        with pytest.raises(ValidationError):
            PlayerFactory(name=None, user=None)

    @pytest.mark.django_db
    def test_delete_player_user(self, user, user_player):
        username = user.username
        assert str(user_player) == username
        assert user_player.name == None
        user.delete()
        user_player.refresh_from_db()
        assert user_player.name == username
        assert user_player.user == None
