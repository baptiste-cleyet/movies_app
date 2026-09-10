def test_index(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"movie-grid" in r.data

def test_watchlist(client):
    r = client.get("/watchlist")
    assert r.status_code == 200

def test_movie_detail_404(client):
    r = client.get("/9999999")
    assert r.status_code == 404

def test_search_exempt(client):
    r = client.post("/search_movie", json={"title": ""})
    assert r.status_code == 400
    assert "requis" in r.get_json()["error"]

def test_add_movie_csrf_disabled(client):
    # with CSRF disabled in fixture, no token needed, but missing fields -> 400
    r = client.post("/add_movie", data={})
    assert r.status_code == 400

def test_search_movie_success(monkeypatch, client):
    import app.routes.api as api_mod
    def fake_search(title):
        return [{"id": 123, "title": "Fake", "poster_path": "/a.jpg"}]
    monkeypatch.setattr(api_mod, "search_movie", fake_search)
    r = client.post("/search_movie", json={"title": "fake"})
    assert r.status_code == 200
    assert "results" in r.get_json()

def test_add_movie_success(monkeypatch, client, app):
    import app.routes.api as api_mod
    def fake_info(mid):
        return {"title": "T", "poster": "p", "year": "2020", "average_rating": 75, "genres": ["Action"], "director": "D", "runtime": "2h", "banner": "b"}
    monkeypatch.setattr(api_mod, "get_movie_info", fake_info)
    r = client.post("/add_movie", data={"movie_add": "123", "rating": "80", "date": "2024-01-01", "summary": "s", "review": "r"})
    assert r.status_code in (302, 303)
    assert r.headers["Location"].endswith("/123")
    # duplicate add should update
    r2 = client.post("/add_movie", data={"movie_add": "123", "rating": "90"})
    assert r2.status_code in (302, 303)

def test_add_movie_invalid_date(monkeypatch, client):
    import app.routes.api as api_mod
    monkeypatch.setattr(api_mod, "get_movie_info", lambda mid: {"title": "T", "poster": "p", "year": "2020", "average_rating": 75, "genres": [], "director": "D", "runtime": "2h", "banner": "b"})
    r = client.post("/add_movie", data={"movie_add": "124", "date": "2024-13-40"})
    assert r.status_code == 400
    assert "Date invalide" in r.get_json()["error"]

def test_add_movie_get_not_allowed(client):
    r = client.get("/add_movie")
    assert r.status_code == 405

def test_update_and_delete_movie(monkeypatch, client, app):
    import app.routes.api as api_mod
    from app.models import Movie
    monkeypatch.setattr(api_mod, "get_movie_info", lambda mid: {"title": "T", "poster": "p", "year": "2020", "average_rating": 75, "genres": [], "director": "D", "runtime": "2h", "banner": "b"})
    client.post("/add_movie", data={"movie_add": "200", "rating": "70"})
    r = client.post("/update_movie/200", data={"rating": "85", "date": "2023-12-01", "summary": "new", "review": "ok"})
    assert r.status_code in (302, 303)
    with app.app_context():
        from app.extensions import db as _db
        assert _db.session.get(Movie, 200).rating == 85
    r2 = client.post("/delete_movie/200")
    assert r2.status_code in (302, 303)
    assert r2.headers["Location"] == "/"

def test_watchlist_add_and_delete(monkeypatch, client, app):
    import app.routes.api as api_mod
    monkeypatch.setattr(api_mod, "get_movie_info", lambda mid: {"title": "WL", "poster": "p", "year": "2021", "average_rating": 70, "genres": [], "director": None, "runtime": None, "banner": None})
    r = client.post("/add_movie_watchlist", data={"movie_add": "300"})
    assert r.status_code in (302, 303)
    r2 = client.post("/delete_movie_watchlist/300")
    assert r2.status_code == 204

def test_search_movie_too_long(client):
    r = client.post("/search_movie", json={"title": "a" * 201})
    assert r.status_code == 400
    assert "trop long" in r.get_json()["error"]
