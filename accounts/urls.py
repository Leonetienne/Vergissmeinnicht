from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("login/2fa", views.twofa_view, name="login_2fa"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/backdrop", views.backdrop_view, name="backdrop"),
]
