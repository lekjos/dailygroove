from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.models import Round
from core.models.factories import (
    GameFactory,
    PlayerFactory,
    SubmissionFactory,
    UserFactory,
)
from core.models.game import Game
from core.models.submission import Submission


class Command(BaseCommand):
    help = "Creates a game and submissions for local development & testing"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete all data before creating test game",
        )

    def handle(self, *args, **options):
        if options["delete"]:
            for model in [Game, Submission, Round]:
                model.objects.all().delete()

        if not settings.DEBUG:
            raise CommandError("This command may only be run in debug mode")

        user = UserFactory(
            username="admin",
            email="admin@admin.admin",
            password="test",
            is_superuser=True,
        )

        player = PlayerFactory(user=user)

        game = GameFactory(
            name="Test Game", slug="test-game", owner=player, players=[player]
        )

        submissions = SubmissionFactory.create_batch(5, games=[game])

        rounds = []
        for i, submission in enumerate(submissions):
            rounds.append(
                Round(
                    game=game, submission=submission, winner=player, round_number=i + 1
                )
            )

        Round.objects.bulk_create(rounds)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created test game: {game.name}")
        )
