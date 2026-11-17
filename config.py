import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
SITE_PASSWORD = os.getenv("SITE_PASSWORD")
# Session persistante 30j + cookie sécurisé (le site est servi en HTTPS).
PERMANENT_SESSION_LIFETIME_DAYS = 30
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
DATABASE = os.path.join(BASE_DIR, "data", "database.db")
# Ensure data directory exists for SQLite
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{DATABASE}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"timeout": 30}}
WTF_CSRF_ENABLED = True
# Derrière le reverse proxy alwaysdata, exiger le header Referer casse des
# clients légitimes (fetch sans Referer). Les tokens CSRF restent vérifiés.
WTF_CSRF_SSL_STRICT = False
TMDB_LANGUAGE = os.getenv("TMDB_LANGUAGE", "fr-FR")
# Authentication journal (app/auth_log.py): JSON lines, "off" disables it.
AUTH_LOG_PATH = os.getenv("AUTH_LOG_PATH") or os.path.join(BASE_DIR, "data", "auth.log")
