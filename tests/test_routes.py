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
    from app import movie_info_request
    def fake_search(title):
        return [{"id": 123, "title": "Fake", "poster_path": "/a.jpg"}]
    monkeypatch.setattr(movie_info_request, "search_movie", fake_search)
    r = client.post("/search_movie", json={"title": "fake"})
    assert r.status_code == 200
    assert "results" in r.get_json()
