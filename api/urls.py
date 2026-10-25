from django.urls import path, re_path

from . import mcp, rest

urlpatterns = [
    path("docs/", rest.docs),
    *rest.urlpatterns_for_registry(),
    re_path(r"^.*$", rest.handler404),
]

mcp_urlpatterns = [path("mcp", mcp.endpoint)]
