# Generated by Django 3.2.20 on 2023-07-19 04:12

import datetime
import uuid

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import timezone_field.fields

import core.models.user


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required--This is your in-game display name. 150 characters or fewer. Letters, spaces, digits and @/./+/-/_ only.",
                        max_length=150,
                        null=True,
                        validators=[core.models.user.UserNameValidator()],
                        verbose_name="username",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("email_confirmed", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.Permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Game",
            fields=[
                ("name", models.CharField(max_length=256)),
                ("slug", models.SlugField(primary_key=True, serialize=False)),
                (
                    "frequency",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Manual"),
                            (1, "Daily"),
                            (2, "Weekdays"),
                            (3, "Weekly"),
                            (4, "Monthly"),
                        ],
                        default=2,
                    ),
                ),
                ("timezone", timezone_field.fields.TimeZoneField(use_pytz=False)),
                ("round_start_time", models.TimeField(default=datetime.time(10, 0))),
                ("invite_token", models.UUIDField(default=uuid.uuid4)),
            ],
        ),
        migrations.CreateModel(
            name="GameSubmission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.game"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=256, null=True)),
                ("role", models.PositiveSmallIntegerField(default=1)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.URLField(blank=True, max_length=1024, null=True)),
                ("type", models.PositiveSmallIntegerField(default=0, editable=False)),
                ("title", models.CharField(blank=True, max_length=512, null=True)),
                ("datetime", models.DateTimeField(auto_now_add=True)),
                (
                    "games",
                    models.ManyToManyField(
                        related_name="submissions",
                        through="core.GameSubmission",
                        to="core.Game",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Round",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "round_number",
                    models.PositiveIntegerField(blank=True, editable=False),
                ),
                ("datetime", models.DateTimeField(auto_now_add=True)),
                (
                    "game",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="core.game"
                    ),
                ),
                (
                    "moderator",
                    models.ForeignKey(
                        blank=True,
                        help_text="what user recorded the winner",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="moderated_rounds",
                        to="core.player",
                    ),
                ),
                (
                    "submission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rounds",
                        to="core.submission",
                    ),
                ),
                (
                    "winner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wins",
                        to="core.player",
                    ),
                ),
            ],
            options={
                "unique_together": {("round_number", "game")},
            },
        ),
        migrations.AddField(
            model_name="gamesubmission",
            name="round",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="core.round",
            ),
        ),
        migrations.AddField(
            model_name="gamesubmission",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.submission"
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_games",
                to="core.player",
            ),
        ),
        migrations.AddField(
            model_name="game",
            name="players",
            field=models.ManyToManyField(to="core.Player"),
        ),
        migrations.AlterUniqueTogether(
            name="gamesubmission",
            unique_together={("game", "submission")},
        ),
    ]
