from flask import Blueprint, render_template, abort
from app.extensions import db
from app.models import Movie, Watchlist
from app.menu import DARK_MODE_ITEMS, SORT_ITEMS_MOVIES, SORT_ITEMS_WATCHLIST, get_detail_menu

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    rows = Movie.query.with_entities(Movie.date, Movie.title, Movie.rating, Movie.year, Movie.tmdb_id, Movie.poster).order_by(Movie.date.desc()).all()
    movies = [dict(zip(["date", "title", "rating", "year", "tmdb_id", "poster"], r)) for r in rows]
    menuItems = [
        {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS
    return render_template("movie_grid.html", movies=movies, menuItems=menuItems, sortItems=SORT_ITEMS_MOVIES)


@bp.route("/watchlist")
def watchlist():
    rows = Watchlist.query.with_entities(Watchlist.tmdb_id, Watchlist.title, Watchlist.poster, Watchlist.year, Watchlist.rating).all()
    movies = [dict(zip(["tmdb_id", "title", "poster", "year", "rating"], r)) for r in rows]
    menuItems = [
        {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS
    return render_template("watchlist.html", movies=movies, menuItems=menuItems, sortItems=SORT_ITEMS_WATCHLIST)


@bp.route("/<int:tmdb_id>")
def movie_detail(tmdb_id):
    movie = db.session.get(Movie, tmdb_id)
    if not movie:
        abort(404)
    movie_dict = movie.to_dict()
    genres = [g.genre for g in movie.genres]
    menuItems = get_detail_menu(tmdb_id)
    return render_template("movie_detail.html", movie=movie_dict, menuItems=menuItems, genres=genres)
