import types

def test_search_movie_empty(monkeypatch):
    from app.movie_info_request import search_movie
    assert search_movie("") == []
    assert search_movie("   ") == []

def test_get_movie_info_uses_two_calls(monkeypatch):
    from app import movie_info_request as mod
    calls = []
    def fake_request(url, params=None):
        calls.append(url)
        if "credits" in url:
            return {"crew": [{"job": "Director", "name": "Dir"}]}
        return {"title": "T", "poster_path": "/p.jpg", "backdrop_path": "/b.jpg", "release_date": "2020-01-01", "runtime": 125, "vote_average": 7.5, "genres": [{"name": "Action"}]}
    monkeypatch.setattr(mod, "_request", fake_request)
    info = mod.get_movie_info(123)
    assert len(calls) == 2
    assert info["director"] == "Dir"
    assert info["runtime"] == "2h 05min"
    assert info["average_rating"] == 75
