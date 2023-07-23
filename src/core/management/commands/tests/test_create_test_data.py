from io import StringIO

from django.core.management import call_command

import pytest

from core.models.game import Game


class TestMgMtCommandCreateTestData:
    @pytest.fixture
    def command_output(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "create_test_data",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    @pytest.mark.django_db
    def test_it_returns_success(self, command_output):
        game = Game.objects.first()
        assert command_output == f"Successfully created test game: {game.name}\n"
