import requests
import os
from functools import lru_cache
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv
from config import TMDB_LANGUAGE

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    # Fail fast with clear message; defer raise until used if needed for import-time tests
    pass

_session = requests.Session()
# Retry on 429/5xx with backoff
_retry = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET"])
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.mount("http://", HTTPAdapter(max_retries=_retry))
TIMEOUT = 5


def _request(url, params=None):
    """Helper with timeout and consistent params."""
    default_params = {"api_key": API_KEY, "language": TMDB_LANGUAGE}
    if params:
        default_params.update(params)
    resp = _session.get(url, params=default_params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_API_movie_details(movie_id):
    """Get the movie details from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    return _request(url)


def _fetch_credits(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
    return _request(url)


def _extract_director(credits):
    for member in credits.get("crew", []):
        if member.get("job") == "Director":
            return member.get("name")
    return None


# Keep public alias for backward compat
def director(tmdb_id):
    try:
        credits = _fetch_credits(tmdb_id)
        return _extract_director(credits)
    except requests.RequestException:
        return None


def search_movie(title):
    """Search a movie in the API from its title. Returns [] if no results."""
    if not title or not title.strip():
        return []
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "query": title.strip(),
        "include_adult": False,
    }
    try:
        data = _request(url, params=params)
    except requests.RequestException:
        return []
    results = data.get("results") or []
    return results[:3]


@lru_cache(maxsize=128)
def get_movie_info(movie_id):
    """Get the movie info from TMDB API. Uses 2 HTTP calls max. Cached 128 entries."""
    try:
        film = get_API_movie_details(movie_id)
    except requests.RequestException:
        return None
    if not film:
        return None

    try:
        credits = _fetch_credits(movie_id)
        director_name = _extract_director(credits)
    except requests.RequestException:
        director_name = None

    runtime_val = film.get("runtime")
    runtime_str = f"{runtime_val // 60}h {runtime_val % 60:02d}min" if runtime_val else None

    vote = film.get("vote_average")
    average_rating = round(vote * 10) if isinstance(vote, (int, float)) else None

    info = {
        "title": film.get("title") or None,
        "poster": "https://image.tmdb.org/t/p/w500" + film["poster_path"] if film.get("poster_path") else None,
        "banner": "https://image.tmdb.org/t/p/w1280" + film["backdrop_path"] if film.get("backdrop_path") else None,
        "tmdb_id": int(movie_id),
        "average_rating": average_rating,
        "year": film.get("release_date", "").split("-")[0] if film.get("release_date") else None,
        "director": director_name,
        "runtime": runtime_str,
        "genres": [g["name"] for g in film.get("genres", [])],
    }
    return info
