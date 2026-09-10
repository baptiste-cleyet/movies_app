from flask import Blueprint, render_template, abort
from app.extensions import db
from app.models import Movie, Watchlist
from app.menu import DARK_MODE_ITEMS, SORT_ITEMS_MOVIES, SORT_ITEMS_WATCHLIST, get_detail_menu

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    movies = Movie.query.order_by(Movie.date.desc()).all()
    movies = [m.to_dict() for m in movies]
    # filter to needed fields for template
    movies = [{k: m[k] for k in ("date", "title", "rating", "year", "tmdb_id", "poster")} for m in movies]
    menuItems = [
        {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS
    return render_template("movie_grid.html", movies=movies, menuItems=menuItems, sortItems=SORT_ITEMS_MOVIES)


@bp.route("/watchlist")
def watchlist():
    movies = [m.to_dict() for m in Watchlist.query.all()]
    menuItems = [
        {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS
    return render_template("watchlist.html", movies=movies, menuItems=menuItems, sortItems=SORT_ITEMS_WATCHLIST)


@bp.route("/<int:tmdb_id>")
def movie_detail(tmdb_id):
    movie = Movie.query.get(tmdb_id)
    if not movie:
        abort(404)
    movie_dict = movie.to_dict()
    genres = [g.genre for g in movie.genres]
    menuItems = get_detail_menu(tmdb_id)
    return render_template("movie_detail.html", movie=movie_dict, menuItems=menuItems, genres=genres)
