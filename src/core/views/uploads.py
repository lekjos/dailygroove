from functools import cached_property

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from core.forms.upload_form import UploadFormAllGames
from core.models.submission import Submission


class UploadsView(LoginRequiredMixin, FormMixin, ListView):
    model = Submission
    form_class = UploadFormAllGames
    template_name = "uploads.html"
    initial = {"url": "https://", "title": ""}
    form_prefix = "upload"

    def get_success_url(self) -> str:
        return reverse("uploads")

    def setup(self, *args, **kwargs):  # pylint: disable=inconsistent-return-statements
        super().setup(*args, **kwargs)
        if not self.request.user.is_authenticated:
            return self.handle_no_permission()
        self.object_list = self.uploads

    @cached_property
    def uploads(self):
        print("here")
        return Submission.objects.filter(user=self.request.user).annotate_fresh()

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
        form = self.get_form()
        print(request.POST)
        if "url" in request.POST:  # pylint: disable=no-else-return
            if form.is_valid():
                form.save()
                return self.form_valid(form)
            return self.form_invalid(form)
        elif "delete-song" in request.POST:
            # TODO delete song
            return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)
