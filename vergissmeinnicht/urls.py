from django.urls import include, path

from api.urls import mcp_urlpatterns

urlpatterns = [
    path("api/v1/", include("api.urls")),
    *mcp_urlpatterns,
    path("", include("accounts.urls")),
    path("", include("boards.urls")),
]
