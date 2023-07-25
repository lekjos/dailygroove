from django.apps import apps
from django.test import Client
from django.urls import reverse_lazy

import pytest

from core.models.factories import UserFactory

TEST_APPS = ["core"]


def admin_models():
    # Get a list of all installed models in the Django project
    all_models = apps.get_models()

    # Filter out models that have registered admin pages
    models_with_admin = []
    for model in all_models:
        app_label = model._meta.app_label
        if (
            app_label in apps.app_configs
            and app_label in TEST_APPS
            and hasattr(model, "_meta")
            and model._meta.managed
        ):
            models_with_admin.append(model)

    return models_with_admin


def modeladmin_test_factory(test_name, model):
    @pytest.mark.django_db
    def test_list_returns_200():
        # Your test logic here
        client = Client()
        user = UserFactory(is_superuser=True, is_staff=True)
        client.force_login(user)
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        response = client.get(
            reverse_lazy(f"admin:{app_label}_{model_name}_changelist")
        )
        assert response.status_code == 200

    test_list_returns_200.__name__ = (
        test_name  # Set the test function's name to the specified test_name
    )
    return test_list_returns_200


for model in admin_models():
    test_name = f"test_modeladmin_list_view_for_{model.__name__}"
    globals()[test_name] = modeladmin_test_factory(test_name, model)
