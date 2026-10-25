from django.conf import settings

from api.rest import api_routes


def app(request):
    context = {
        "APP_VERSION": settings.APP_VERSION,
        "REPOSITORY_URL": settings.REPOSITORY_URL,
        "ENABLE_REGISTRATION": settings.ENABLE_REGISTRATION,
        "EMAIL_CONFIGURED": settings.EMAIL_CONFIGURED,
    }
    if request.user.is_authenticated:
        context["api_routes"] = api_routes()
    return context
