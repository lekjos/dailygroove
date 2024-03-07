from functools import cached_property

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin, ProcessFormView

from core.forms.upload_form import UploadFormAllGames
from core.models.submission import Submission


class UploadsView(LoginRequiredMixin, FormMixin, ProcessFormView, ListView):
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
        return Submission.objects.filter(user=self.request.user).annotate_fresh()

    def get_form(self, form_class=None):
        return UploadFormAllGames(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()

        ctx = super().get_context_data(**kwargs)
        ctx["object_list"] = self.uploads
        return ctx

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        if "delete-upload" in request.POST:
            return self.handle_upload_delete(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def handle_upload_delete(self, *args, **kwargs):
        submission = Submission.objects.get(id=self.request.POST["delete-upload"])
        if not submission.pk in [x.id for x in self.uploads]:
            raise PermissionDenied("You cannot delete a song you don't own.")
        submission.delete()
        messages.success(
            self.request,
            f"You have successfully removed {submission.title or submission.url}",
        )
        return HttpResponseRedirect(self.get_success_url())
