"""Protection globale du site par mot de passe unique.

Le mot de passe est fourni via la variable d'environnement SITE_PASSWORD
(config.py). Il est haché une seule fois par processus au démarrage
(werkzeug PBKDF2) puis vérifié avec check_password_hash.
"""

import os
import time
import warnings

from flask import current_app, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

SESSION_KEY = "authed"
MAX_ATTEMPTS = 10
WINDOW_SECONDS = 600


def init_auth(app):
    """Hache le mot de passe du site au démarrage. Fail fast en production."""
    password = app.config.get("SITE_PASSWORD")
    if not password:
        if app.config.get("TESTING"):
            password = "test-password-not-for-production"
        elif os.getenv("FLASK_ENV") == "production":
            raise RuntimeError(
                "SITE_PASSWORD is not set. "
                "Set it in the alwaysdata site environment variables."
            )
        else:
            warnings.warn(
                "SITE_PASSWORD not set, using dev fallback. Set it for production.",
                UserWarning,
            )
            password = "dev-only-change-me"
    app.config["PASSWORD_HASH"] = generate_password_hash(password)
    app.config.setdefault("_login_attempts", {})


def is_authenticated():
    return session.get(SESSION_KEY) is True


def _client_ip():
    # Derrière le reverse proxy alwaysdata, l'IP réelle est transmise via X-Forwarded-For.
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _prune_attempts(store, now):
    cutoff = now - WINDOW_SECONDS
    for ip in list(store.keys()):
        store[ip] = [t for t in store[ip] if t > cutoff]
        if not store[ip]:
            del store[ip]


def is_rate_limited():
    store = current_app.config["_login_attempts"]
    now = time.monotonic()
    _prune_attempts(store, now)
    return len(store.get(_client_ip(), [])) >= MAX_ATTEMPTS


def record_failed_attempt():
    store = current_app.config["_login_attempts"]
    now = time.monotonic()
    _prune_attempts(store, now)
    store.setdefault(_client_ip(), []).append(now)


def clear_attempts():
    current_app.config["_login_attempts"].pop(_client_ip(), None)


def verify_password(candidate):
    if not candidate:
        return False
    return check_password_hash(current_app.config["PASSWORD_HASH"], candidate)


def safe_next(value):
    """N'autorise que les redirections internes (anti open-redirect)."""
    if value and value.startswith("/") and not value.startswith("//"):
        return value
    return None


def register_guard(app):
    @app.before_request
    def require_auth():
        if request.endpoint in ("auth.login", "static"):
            return None
        if is_authenticated():
            return None
        # Les appels API (fetch JS) reçoivent du JSON, pas une redirection HTML.
        if request.blueprint == "api":
            return jsonify({"error": "Authentification requise."}), 401
        return redirect(url_for("auth.login", next=request.full_path))
