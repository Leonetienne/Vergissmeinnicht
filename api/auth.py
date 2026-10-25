from accounts.models import Key


def bearer_token(request):
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if header[:7].lower() == "bearer ":
        return header[7:].strip()
    return None


def key_user(request, kind):
    token = bearer_token(request)
    return Key.authenticate(token, kind) if token else None
