import json
import os

from wsgi import create_app

KEYS = ["ts", "site", "event", "ip", "xff", "ua", "method", "path"]


def read_journal(app):
    with open(app.config["AUTH_LOG_PATH"], encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def test_login_success_and_failure_are_logged(anon_client, app):
    anon_client.post("/login", data={"password": "nope"}, headers={"User-Agent": "pytest-ua"})
    anon_client.post("/login", data={"password": "test-password"})
    lines = read_journal(app)
    assert [line["event"] for line in lines] == ["login_failure", "login_success"]
    assert list(lines[0].keys()) == KEYS
    assert lines[0]["site"] == "movies"
    assert lines[0]["ua"] == "pytest-ua"
    assert lines[0]["method"] == "POST" and lines[0]["path"] == "/login"


def test_unauthenticated_access_is_logged(anon_client, app):
    anon_client.get("/watchlist")
    anon_client.post("/search_movie", json={"title": "x"})
    events = [(line["event"], line["path"]) for line in read_journal(app)]
    assert events == [("unauthenticated", "/watchlist"), ("unauthenticated", "/search_movie")]


def test_login_page_itself_is_not_logged(anon_client, app):
    anon_client.get("/login")
    assert not os.path.exists(app.config["AUTH_LOG_PATH"]) or read_journal(app) == []


def test_rate_limited_is_logged(anon_client, app):
    for _ in range(11):
        anon_client.post("/login", data={"password": "nope"})
    events = [line["event"] for line in read_journal(app)]
    assert events.count("login_failure") == 10
    assert events[-1] == "rate_limited"


def test_ip_comes_from_x_real_ip_not_forwarded_for(anon_client, app):
    anon_client.post(
        "/login",
        data={"password": "nope"},
        headers={"X-Real-IP": "5.6.7.8", "X-Forwarded-For": "1.2.3.4"},
    )
    line = read_journal(app)[0]
    assert line["ip"] == "5.6.7.8"
    assert line["xff"] == "1.2.3.4"


def test_forged_forwarded_for_does_not_bypass_rate_limit(anon_client, app):
    # Changing X-Forwarded-For must not reset the per-IP failure counter.
    for i in range(10):
        anon_client.post(
            "/login", data={"password": "nope"},
            headers={"X-Real-IP": "5.6.7.8", "X-Forwarded-For": f"9.9.9.{i}"},
        )
    r = anon_client.post(
        "/login", data={"password": "nope"},
        headers={"X-Real-IP": "5.6.7.8", "X-Forwarded-For": "9.9.9.99"},
    )
    assert r.status_code == 429


def test_journal_off(tmp_path):
    app = create_app(
        test_config={
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'db.sqlite'}",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret",
            "SITE_PASSWORD": "test-password",
            "AUTH_LOG_PATH": "off",
        }
    )
    app.test_client().post("/login", data={"password": "nope"})
    assert app.extensions["auth_log"] is None
    assert not any(p.name.endswith(".log") for p in tmp_path.iterdir())
