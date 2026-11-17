import os
import tempfile
import pytest
from wsgi import create_app
from app.extensions import db as _db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
        "SITE_PASSWORD": "test-password",
        "AUTH_LOG_PATH": db_path + ".auth.log",
    }
    app = create_app(test_config=config)
    with app.app_context():
        _db.create_all()
    yield app
    os.close(db_fd)
    os.unlink(db_path)
    for suffix in ("", ".1", ".2", ".3"):
        if os.path.exists(db_path + ".auth.log" + suffix):
            os.unlink(db_path + ".auth.log" + suffix)

@pytest.fixture
def client(app):
    # Client authentifié par défaut : les tests existants couvrent le comportement connecté.
    c = app.test_client()
    c.post("/login", data={"password": "test-password"})
    return c

@pytest.fixture
def anon_client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
