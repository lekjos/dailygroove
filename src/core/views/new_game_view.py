import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin, ProcessFormView

from core.forms.game_detail_form import NewGameDetailForm
from core.forms.player_invite_form import EmailFormSet
from core.models.game import Game
from core.models.player import Player
from core.utils.player_invite import send_invite_emails

logger = logging.getLogger(__name__)


class NewGameView(LoginRequiredMixin, FormMixin, ProcessFormView, TemplateView):
    model = Game
    template_name = "new-game.html"
    form_class = NewGameDetailForm

    def get_success_url(self) -> str:
        return reverse("dashboard")

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data()
        ctx["email_formset"] = EmailFormSet(prefix="emails")
        return ctx

    def forms_invalid(self, game_form, email_formset):
        """If the form is invalid, render the invalid form."""
        for form in email_formset:
            print(f"{form} valid:{form.is_valid()}")
        return self.render_to_response(
            self.get_context_data(form=game_form, email_formset=email_formset)
        )

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        email_formset = EmailFormSet(request.POST, prefix="emails")
        if form.is_valid() and email_formset and email_formset.is_valid():
            return self.forms_valid(form, email_formset)
        return self.forms_invalid(form, email_formset)

    def forms_valid(self, game_form: NewGameDetailForm, email_formset):
        game: Game = game_form.save(commit=False)
        game.slug = slugify(game.name)
        game.owner = self.request.user
        game.save()
        Player.objects.create(
            game=game, user=self.request.user, role=Player.Roles.MODERATOR
        )
        if email_formset:
            recipients = []
            for form in email_formset:
                email = form.cleaned_data.get("recipient_email", "")
                if email:
                    recipients.append(email)

            if recipients:
                send_invite_emails(
                    self.request,
                    game=game,
                    sender=self.request.user,
                    recipient_list=recipients,
                )
        return HttpResponseRedirect(self.get_success_url())
