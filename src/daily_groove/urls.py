"""
URL configuration for daily_groove project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from core import views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("", views.Dashboard.as_view(), name="dashboard"),
    path("uploads/", views.UploadsView.as_view(), name="uploads"),
    path("signup/", views.signup_view, name="signup"),
    path("g/new/", views.NewGameView.as_view(), name="new_game"),
    path(
        "account_activation_sent/",
        views.account_activation_sent_view,
        name="account_activation_sent",
    ),
    path(
        "activate/<str:uidb64>/<str:token>/", views.activate_view, name="activate"
    ),  # HARDCODED IN invite_token_middleware.py, ALSO UPDATE THERE
    path("g/<slug:slug>/", views.GameView.as_view(), name="game_detail"),
    path("g/<slug:slug>/manage/", views.ManageGameView.as_view(), name="manage_game"),
    path(
        "g/<slug:slug>/invite/", views.PlayerInviteView.as_view(), name="player_invite"
    ),
]

if settings.ENABLE_DEBUG_TOOLBAR:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
