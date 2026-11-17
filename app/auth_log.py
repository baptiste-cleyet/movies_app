"""Authentication journal: one JSON line per authentication event.

Format (shared with the other self-hosted apps, read by the same tooling):
    {"ts": "...+01:00", "site": "movies", "event": "login_failure", "ip": "203.0.113.5",
     "xff": "<raw X-Forwarded-For>", "ua": "<User-Agent>", "method": "POST", "path": "/login"}
Events: login_success, login_failure, rate_limited, unauthenticated.

Destination: config AUTH_LOG_PATH (env var of the same name), default data/auth.log;
"off" disables the journal. Rotated at 5 MB, 3 old files kept. Writing the journal never
breaks a request.
"""

import json
import logging
import logging.handlers
import os
from datetime import datetime

from flask import current_app, request

SITE = "movies"
MAX_BYTES = 5_000_000
BACKUP_COUNT = 3
EXTENSION_KEY = "auth_log"


def client_ip():
    """Client IP behind the alwaysdata reverse proxy: the X-Real-IP header it sets.

    X-Forwarded-For is NOT used: a value sent by the client reaches the app unchanged
    (checked on alwaysdata 2026-11-16), so it can be forged. It is only logged raw ("xff").
    """
    real_ip = request.headers.get("X-Real-IP", "").strip()
    return real_ip or request.remote_addr or "unknown"


def init_auth_log(app):
    """Attach the journal to the app (one unregistered logger per app instance)."""
    path = app.config.get("AUTH_LOG_PATH") or ""
    if path.strip().lower() == "off":
        app.extensions[EXTENSION_KEY] = None
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    logger = logging.Logger(f"{SITE}.auth")
    logger.propagate = False
    handler = logging.handlers.RotatingFileHandler(
        path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8", delay=True
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    app.extensions[EXTENSION_KEY] = logger


def log_auth_event(event):
    """Write one journal line for the current request. Never raises."""
    try:
        logger = current_app.extensions.get(EXTENSION_KEY)
        if logger is None:
            return
        record = {
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
            "site": SITE,
            "event": event,
            "ip": client_ip(),
            "xff": request.headers.get("X-Forwarded-For", "")[:300],
            "ua": request.headers.get("User-Agent", "")[:300],
            "method": request.method,
            "path": request.path[:200],
        }
        logger.info(json.dumps(record, ensure_ascii=False))
    except Exception:  # noqa: BLE001 - the journal must never break a request
        pass
