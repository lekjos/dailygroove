from functools import cached_property
from typing import Any, Dict

from django.db.models import Prefetch
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from core.forms.upload_form import UploadFormAllGames
from core.models.game import Game
from core.models.submission import Submission


class UploadsView(FormMixin, ListView):
    model = Submission
    form_class = UploadFormAllGames
    template_name = "uploads.html"
    initial = {"url": "https://", "title": ""}
    form_prefix = "upload"

    def get_success_url(self) -> str:
        return reverse("uploads")

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.object_list = self.uploads

    @cached_property
    def uploads(self):
        print("here")
        return Submission.objects.filter(user=self.request.user).prefetch_related(
            "games"
        )

    def get_form(self, form_class=None):
        return UploadFormAllGames(self.request.user, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()

        ctx = super().get_context_data(**kwargs)
        # if "object_list" not in ctx:
        ctx["object_list"] = self.uploads
        return ctx

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""

        return self.render_to_response(
            self.get_context_data(form=form, object_list=self.uploads)
        )

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        print(request.POST)
        if "url" in request.POST:
            form = self.get_form()
            if form.is_valid():
                form.save()
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        elif "delete-song" in request.POST:
            # TODO delete song
            pass

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
