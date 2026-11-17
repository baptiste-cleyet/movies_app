from flask import Blueprint, redirect, render_template, request, session, url_for

from app.auth import (
    SESSION_KEY,
    clear_attempts,
    is_rate_limited,
    record_failed_attempt,
    safe_next,
    verify_password,
)
from app.auth_log import log_auth_event

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if is_rate_limited():
            log_auth_event("rate_limited")
            return render_template(
                "login.html",
                menuItems=[],
                error="Trop de tentatives. Réessaie dans quelques minutes.",
            ), 429
        if verify_password(request.form.get("password", "")):
            log_auth_event("login_success")
            clear_attempts()
            session.clear()
            session.permanent = True
            session[SESSION_KEY] = True
            target = safe_next(request.form.get("next") or request.args.get("next"))
            return redirect(target or url_for("main.index"))
        log_auth_event("login_failure")
        record_failed_attempt()
        return render_template(
            "login.html", menuItems=[], error="Mot de passe incorrect."
        ), 401
    return render_template("login.html", menuItems=[])


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
