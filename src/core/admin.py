from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import BooleanField, Count, ExpressionWrapper, Q, QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from core.models import Game, Player, Round, Submission
from core.models.user import User
from core.utils import IsNullFilter


class PlayerInline(admin.TabularInline):
    model = Player


class PlayerIsNullFilter(IsNullFilter):
    title = "Has Bound Player(s)"
    parameter_name = "has_player"
    field_lookup = "player"


@admin.register(User)
class UserAdminCustom(UserAdmin):
    list_display = (
        "username",
        "email",
        "email_confirmed",
        "is_staff",
    )
    search_fields = ("username", "email")
    list_filter = (PlayerIsNullFilter, "email_confirmed")

    inlines = [PlayerInline]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email", "email_confirmed")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class UserIsNullFilter(IsNullFilter):
    title = "Has Bound User"
    parameter_name = "has_user"
    field_lookup = "user"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_filter = (UserIsNullFilter,)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        return qs.annotate(
            anonymous=ExpressionWrapper(Q(name=None), output_field=BooleanField())
        )


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "player_count", "round_count")
    inlines = [PlayerInline]

    def player_count(self, obj):
        return obj.player_count

    def round_count(self, obj):
        return obj.round_count

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        return qs.annotate(
            player_count=Count("players", distinct=True),
            round_count=Count("round", distinct=True),
        )


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = (
        "round_number",
        "game",
        "winner",
    )
    search_fields = (
        "game__name",
        "game__pk",
    )
    list_filter = ("game",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "url",
    )
    search_fields = ("url", "user__username", "title")
    list_filter = ("user",)
