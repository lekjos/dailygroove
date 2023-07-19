from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserNameValidator(UnicodeUsernameValidator):
    regex = r"^[\w.@+ -]+\Z"
    message = message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and @/./+/-/_, and the space character."
    )


class UserManagerCustom(UserManager):
    def create_superuser(self):
        super().create_superuser()


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UserNameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        null=True,
        help_text=_(
            "Required--This is your in-game display name. 150 characters or fewer. Letters, spaces, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _("email address"), unique=True, primary_key=True, blank=True
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f"{str(self.username)} ({str(self.pk)})"

    def delete(self, *args, **kwargs):
        from ..models.player import Player

        Player.objects.filter(user=self).update(name=self.username)
        super().delete(*args, **kwargs)
