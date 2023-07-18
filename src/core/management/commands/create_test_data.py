import random
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.models import Round, User
from core.models.factories import GameFactory, PlayerFactory, SubmissionFactory
from core.models.game import Game
from core.models.game_submission import GameSubmission
from core.models.player import Player
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
        if not settings.DEBUG:
            raise CommandError("This command may only be run in debug mode")

        if options["delete"]:
            for model in [Game, Submission, Round, User, Player, GameSubmission]:
                model.objects.all().delete()

        user = User.objects.create_superuser(
            username="admin",
            email="admin@admin.admin",
            password="test",
        )
        admin_player = PlayerFactory(user=user, name=None)

        players = PlayerFactory.create_batch(5)

        game = GameFactory(
            name="Test Game",
            slug="test-game",
            owner=admin_player,
            players=players + [admin_player],
        )

        submissions = SubmissionFactory.create_batch(15, games=[game])

        round_num = 0
        for i, submission in enumerate(submissions):
            if i <= 10:
                continue
            r = Round.objects.create(
                game=game,
                submission=submission,
                winner=random.choice(players),
            )
            GameSubmission.objects.filter(game=game, submission=submission).update(
                round=r
            )
            round_num += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created test game: {game.name}")
        )

        for i, rnd in enumerate(
            Round.objects.filter(game=game).order_by("round_number")
        ):
            rnd.datetime = timezone.now() - timedelta(days=len(submissions) - i)
            rnd.save()
