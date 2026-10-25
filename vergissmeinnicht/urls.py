from django.conf import settings
from django.http import HttpResponseServerError
from django.template import loader
from django.urls import include, path

from api.urls import mcp_urlpatterns

urlpatterns = [
    path("api/v1/", include("api.urls")),
    *mcp_urlpatterns,
    path("", include("accounts.urls")),
    path("", include("boards.urls")),
]


def server_error(request):
    # No request context: its processors may touch the database that just failed.
    context = {"APP_VERSION": settings.APP_VERSION, "REPOSITORY_URL": settings.REPOSITORY_URL}
    return HttpResponseServerError(loader.get_template("500.html").render(context))


handler500 = server_error
