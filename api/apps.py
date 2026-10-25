from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"

    def ready(self):
        from . import operations  # noqa: F401  registers the handlers
