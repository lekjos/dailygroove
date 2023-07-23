import random
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

import factory

from core.models import Round, User
from core.models.factories import GameFactory, PlayerFactory, SubmissionFactory
from core.models.game import Game
from core.models.player import Player
from core.models.submission import Submission

YOUTUBE_LINKS = [
    (None, "https://www.youtube.com/watch?v=9bZkp7q19f0"),
    ("My heart will go on", "https://www.youtube.com/watch?v=Qf4zY6diTwQ"),
    ("Thriller", "http://youtu.be/sOnqjkJTMaA"),
    ("Born in the USA", "https://www.youtube.com/watch?v=EPhWR4d3FJQ"),
    (None, "https://www.youtube.com/watch?v=vx-Lzo9NxAQ"),
    (None, "https://www.youtube.com/watch?v=QkiAwT3b2FI"),
    (None, "https://m.youtube.com/watch?v=yV2zyKYWcTQ?t=60"),
    ("JT Mirrors", "https://youtu.be/uuZE_IRwLNI"),
    (
        "daylight",
        "https://open.spotify.com/track/1odExI7RdWc4BT515LTAwj?si=e3936aab8c5748c1",
    ),
]


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
            for model in [Game, Submission, Round, User, Player]:
                model.objects.all().delete()

        user = User.objects.create_superuser(
            username="admin",
            email="admin@admin.admin",
            password="test",
        )

        game = GameFactory(
            name="Test Game",
            slug="test-game",
            owner=user,
        )
        admin_player = PlayerFactory(user=user, name=None, game=game)

        players = PlayerFactory.create_batch(5, game=game)

        users = User.objects.filter(player__in=list(players) + [admin_player])

        submissions = []
        submissions_len = len(YOUTUBE_LINKS)
        for title, link in YOUTUBE_LINKS:
            submissions.append(
                SubmissionFactory(
                    user=factory.Iterator(
                        [random.choice(users) for _ in range(submissions_len)]
                    ),
                    title=title,
                    url=link,
                )
            )

        round_num = 0
        for i, submission in enumerate(submissions):
            if i <= 10:
                continue
            Round.objects.create(
                game=game,
                submission=submission,
                winner=random.choice(players),
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
