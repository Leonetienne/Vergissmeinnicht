from django.contrib.auth.views import redirect_to_login

PUBLIC_PATHS = {"/login", "/login/2fa", "/register", "/mcp"}
PUBLIC_PREFIXES = ("/api/", "/static/")


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if not request.user.is_authenticated and path not in PUBLIC_PATHS and not path.startswith(PUBLIC_PREFIXES):
            return redirect_to_login(request.get_full_path(), "/login")
        return self.get_response(request)
