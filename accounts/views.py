from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from boards.services import ServiceError

from . import services as acc
from .models import Key, User

PENDING_USER = "pending_2fa_user"
PENDING_NEXT = "pending_2fa_next"
PENDING_SECRET = "pending_totp_secret"


def _safe_next(request, value):
    if value and url_has_allowed_host_and_scheme(value, {request.get_host()}, require_https=False):
        return value
    return "/"


def login_view(request):
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    context = {"next": next_url, "email": ""}
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        context["email"] = email
        if acc.login_blocked(email):
            context["error"] = "Too many attempts, wait 15 minutes"
            return render(request, "accounts/login.html", context, status=429)
        user = authenticate(request, email=email, password=request.POST.get("password", ""))
        if user is None:
            acc.record_failure(email)
            context["error"] = "Email or password is wrong"
            return render(request, "accounts/login.html", context, status=400)
        if user.has_totp:
            request.session[PENDING_USER] = user.pk
            request.session[PENDING_NEXT] = next_url
            return redirect("login_2fa")
        acc.clear_failures(email)
        login(request, user)
        return redirect(_safe_next(request, next_url))
    return render(request, "accounts/login.html", context)


def twofa_view(request):
    user = User.objects.filter(pk=request.session.get(PENDING_USER)).first()
    if user is None:
        return redirect("login")
    context = {}
    if request.method == "POST":
        if acc.login_blocked(user.email):
            context["error"] = "Too many attempts, wait 15 minutes"
            return render(request, "accounts/twofa.html", context, status=429)
        result = acc.verify_second_factor(user, request.POST.get("code", ""))
        if result is None:
            acc.record_failure(user.email)
            context["error"] = "Code is wrong"
            return render(request, "accounts/twofa.html", context, status=400)
        next_url = request.session.get(PENDING_NEXT, "")
        acc.clear_failures(user.email)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        if result == "recovery":
            messages.info(request, "Second factor removed")
        return redirect(_safe_next(request, next_url))
    return render(request, "accounts/twofa.html", context)


def register_view(request):
    if not settings.ENABLE_REGISTRATION:
        raise Http404
    context = {}
    if request.method == "POST":
        context = {k: request.POST.get(k, "") for k in ("display_name", "email")}
        try:
            user = acc.register(context["display_name"], context["email"], request.POST.get("password", ""))
        except ServiceError as e:
            context["error"] = e.message
            return render(request, "accounts/register.html", context, status=400)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("/")
    return render(request, "accounts/register.html", context)


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


def _key_status(user):
    keys = {k.kind: k for k in user.keys.all()}
    return {"api": keys.get(Key.API), "mcp": keys.get(Key.MCP)}


def settings_view(request):
    user = request.user
    context = {}
    if request.method == "POST":
        action = request.POST.get("action", "")
        try:
            result = _settings_action(request, action, context)
        except ServiceError as e:
            context["errors"] = {action: e.message}
            result = None
        if result is not None:
            return result
    context.setdefault("totp_secret", request.session.get(PENDING_SECRET) if not user.has_totp else None)
    if context["totp_secret"]:
        context["totp_qr"] = acc.qr_svg(acc.totp_uri(user, context["totp_secret"]))
    context["keys"] = _key_status(user)
    context["api_base"] = settings.SITE_URL + "/api/v1/"
    context["mcp_endpoint"] = settings.SITE_URL + "/mcp"
    context["appearance"] = {
        "css": user.backdrop_css,
        "cssMobile": user.backdrop_css_mobile,
        "uiOpacity": user.ui_opacity,
        "backdropOpacity": user.backdrop_opacity,
    }
    return render(request, "accounts/settings.html", context)


def _settings_action(request, action, context):
    """Run one settings section. Returns a redirect when done, or None to render with context."""
    user = request.user
    post = request.POST
    if action == "profile":
        acc.update_profile(user, display_name=post.get("display_name", ""), email=post.get("email", ""))
        messages.info(request, "Profile saved")
    elif action == "password":
        if not user.check_password(post.get("current_password", "")):
            raise acc.Invalid("Current password is wrong")
        acc.check_password(post.get("new_password", ""), user)
        user.set_password(post["new_password"])
        user.save()
        update_session_auth_hash(request, user)
        messages.info(request, "Password changed")
    elif action == "notifications":
        acc.update_profile(user, reminders_enabled=post.get("reminders_enabled") == "on")
        messages.info(request, "Notifications saved")
    elif action == "totp_start":
        if not user.has_totp:
            request.session[PENDING_SECRET] = acc.new_totp_secret()
    elif action == "totp_activate":
        secret = request.session.get(PENDING_SECRET)
        if user.has_totp or not secret:
            return redirect("settings")
        codes = acc.activate_totp(user, secret, post.get("code", ""))
        if codes is None:
            raise acc.Invalid("Code is wrong")
        del request.session[PENDING_SECRET]
        context["recovery_codes"] = codes
        context["totp_secret"] = None
        return None
    elif action == "totp_cancel":
        request.session.pop(PENDING_SECRET, None)
    elif action == "totp_remove":
        if acc.verify_second_factor(user, post.get("code", "")) is None:
            raise acc.Invalid("Code is wrong")
        acc.remove_totp(user)
        messages.info(request, "Second factor removed")
    elif action in ("api_generate", "mcp_generate"):
        kind = action[:3]
        context["new_key"] = {"kind": kind, "value": Key.generate(user, kind)}
        return None
    elif action in ("api_revoke", "mcp_revoke"):
        Key.objects.filter(user=user, kind=action[:3]).delete()
        messages.info(request, "Key revoked")
    elif action == "appearance":
        upload = request.FILES.get("backdrop")
        if upload:
            acc.store_backdrop(user, upload)
        acc.update_appearance(
            user, post.get("backdrop_mode"), post.get("backdrop_opacity"),
            post.get("backdrop_css"), post.get("backdrop_css_mobile"), post.get("ui_opacity"),
        )
        messages.info(request, "Appearance saved")
    elif action == "backdrop_remove":
        acc.remove_backdrop(user)
        messages.info(request, "Backdrop removed")
    elif action == "delete_account":
        acc.delete_account(user)
        logout(request)
        return redirect("login")
    else:
        raise acc.Invalid("Unknown action")
    return redirect("settings")


def backdrop_view(request):
    path = acc.backdrop_path(request.user)
    if path is None or not path.exists():
        raise Http404
    response = FileResponse(path.open("rb"))
    response["Cache-Control"] = "private, max-age=86400"
    return response
