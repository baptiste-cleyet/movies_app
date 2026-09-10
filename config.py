import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
DATABASE = os.path.join(BASE_DIR, "data", "database.db")
# Ensure data directory exists for SQLite
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{DATABASE}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"timeout": 30}}
WTF_CSRF_ENABLED = True
TMDB_LANGUAGE = os.getenv("TMDB_LANGUAGE", "fr-FR")
