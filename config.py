import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or "dev-only-change-me"
DATABASE = os.path.join(BASE_DIR, "data", "database.db")
WTF_CSRF_ENABLED = True
