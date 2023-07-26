"""
This module automatically generates a smoke test for all ModelAdmin classes registered in TEST_APPS. That includes:
- confirming the changelist view returns 200
- confirming that using the search bar returns a 200

"""

from typing import List

from django.apps import apps
from django.db import models
from django.test import Client
from django.urls import reverse_lazy

import pytest

from core.models.factories import UserFactory

TEST_APPS = ["core"]


def admin_models() -> List[models.Model]:
    """Returns a list of all installed models in the Django project"""
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


@pytest.fixture
def user():
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def client(user):
    client = Client()
    client.force_login(user)
    return client


def build_search_returns_200(model):
    @pytest.mark.django_db
    def test_search_returns_200(self, client):
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        response = client.get(
            f'{reverse_lazy(f"admin:{app_label}_{model_name}_changelist")}?q=test'
        )
        assert response.status_code == 200

    return test_search_returns_200


def build_test_list_returns_200(model):
    @pytest.mark.django_db
    def test_list_returns_200(self, client):
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        response = client.get(
            reverse_lazy(f"admin:{app_label}_{model_name}_changelist")
        )
        assert response.status_code == 200

    return test_list_returns_200


for model in admin_models():
    test_methods = {
        "test_list_returns_200": build_test_list_returns_200(model),
        "test_search_returns_200": build_search_returns_200(model),
    }

    # generate test class and add methods
    new_class_name = f"Test{str(model.__name__).capitalize()}ModelAdmin"
    new_class = type(new_class_name, (object,), test_methods)

    # save new class to globals so pytest picks it up
    globals()[new_class_name] = new_class
