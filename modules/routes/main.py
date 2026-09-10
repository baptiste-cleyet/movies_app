from flask import Blueprint, render_template, abort
from modules.db import query_fetch
from modules.menu import DARK_MODE_ITEMS, SORT_ITEMS_MOVIES, SORT_ITEMS_WATCHLIST, get_detail_menu

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    movies = query_fetch("SELECT date, title, rating, year, tmdb_id, poster FROM movies ORDER BY date DESC")
    menuItems = [
        {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS
    return render_template("movie_grid.html", movies=movies, menuItems=menuItems, sortItems=SORT_ITEMS_MOVIES)


@bp.route("/watchlist")
def watchlist():
    movies = query_fetch("SELECT * FROM watchlist")
    menuItems = [
        {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS
    return render_template("watchlist.html", movies=movies, menuItems=menuItems, sortItems=SORT_ITEMS_WATCHLIST)


@bp.route("/<int:tmdb_id>")
def movie_detail(tmdb_id):
    movie = query_fetch("SELECT * FROM movies WHERE tmdb_id = ?", params=(tmdb_id,), fetchone=True)
    if not movie:
        abort(404)
    genres = query_fetch("SELECT genre FROM genres WHERE tmdb_id = ?", params=(tmdb_id,))
    menuItems = get_detail_menu(tmdb_id)
    return render_template("movie_detail.html", movie=movie, menuItems=menuItems, genres=[g["genre"] for g in genres])
