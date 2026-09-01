import sqlite3
import os
from flask import Flask, render_template, request, jsonify, redirect
from modules.movie_info_request import get_movie_info, search_movie

app = Flask(__name__)

DARK_MODE_ITEMS = [
    {"id": "dark-mode", "name": "Sombre", "iconName": "moon"},
    {"id": "light-mode", "name": "Clair", "iconName": "sun"},
]

BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
db_path = os.path.join(BASE_DIR, 'data', 'database.db')

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=()):
    conn = get_db_connection()
    conn.execute(query, params)
    conn.commit()
    conn.close()

def execute_query_fetch(query, params=(), fetchone=False):
    conn = get_db_connection()
    result = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in result] if not fetchone else dict(result[0]) if result else None


@app.route('/')
def index():
    movies = execute_query_fetch('SELECT date, title, rating, year, tmdb_id, poster FROM movies ORDER BY date DESC')

    menuItems = [
        {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS

    sortItems = [
        {"id": "date-sort", "name": "Date de visionnage", "iconName": "calendar"},
        {"id": "title-sort", "name": "Titre", "iconName": "type"},
        {"id": "rating-sort", "name": "Note", "iconName": "star"},
        {"id": "year-sort", "name": "Année de sortie", "iconName": "calendar-clock"},
    ]
    
    return render_template('movie_grid.html', movies=movies, menuItems = menuItems, sortItems = sortItems)

@app.route('/watchlist')
def watchlist():
    movies = execute_query_fetch('SELECT * FROM watchlist')

    menuItems = [
        {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
        {"id": "search-button", "name": "Rechercher", "iconName": "search"},
        {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
        {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
    ] + DARK_MODE_ITEMS

    sortItems = [
        {"id": "title-sort", "name": "Titre", "iconName": "type"},
        {"id": "rating-sort", "name": "Note", "iconName": "star"},
        {"id": "year-sort", "name": "Année de sortie", "iconName": "calendar-clock"},
    ]

    return render_template('watchlist.html', movies=movies, menuItems = menuItems, sortItems = sortItems)

@app.route('/<int:tmdb_id>')
def movie_detail(tmdb_id):
    movie = execute_query_fetch('SELECT * FROM movies WHERE tmdb_id = ?', params=(tmdb_id,), fetchone=True)
    genres = execute_query_fetch('SELECT genre FROM genres WHERE tmdb_id = ?', params=(tmdb_id,))
    menuItems = [
        {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
        {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        {"id": "delete-movie-button", "name": "Supprimer", "iconName": "trash-2"},
        {"id": "update-movie-button", "name": "Mettre à jour", "iconName": "pencil"},
        {"id": "tmdb-link", "name": "Page TMDB", "iconName": "square-arrow-out-up-right", "href": f"https://www.themoviedb.org/movie/{tmdb_id}", "mobileOnly": True},
    ] + DARK_MODE_ITEMS
    return render_template('movie_detail.html', movie=movie, menuItems = menuItems, genres=[genre['genre'] for genre in genres])


@app.route('/add_movie', methods=['POST', 'GET'])
def add_movie():
    error = "Un erreur est survenue."
    if request.method == 'POST':
        movie_id = request.form.getlist('movie_add')[0]
        movie_info = get_movie_info(movie_id)
        if not movie_info:
            return jsonify({"error": "Film introuvable."}), 400
        movie_info['rating'] = request.form.getlist('rating')[0]
        movie_info['summary'] = request.form.getlist('summary')[0]
        movie_info['date'] = request.form.getlist('date')[0]
        movie_info['review'] = request.form.getlist('review')[0]
        columns = ("tmdb_id", "title", "poster" , "rating", "date", "year", "summary", "review", "director", "runtime", "average_rating", "banner")
        placeholders = ", ".join(["?"] * len(columns))
        update_clause = ", ".join([f"{c} = excluded.{c}" for c in columns[1:]])  # Exclure tmdb_id de la mise à jour
        query_add = f"""
            INSERT into movies ({", ".join(columns)}) values({placeholders})
            ON CONFLICT(tmdb_id) 
            DO UPDATE SET 
            {update_clause}
            ;
        """
        params = tuple(movie_info[c] for c in columns)
        query_delete_watchlist = 'DELETE FROM watchlist WHERE tmdb_id = ?'
        try:
            execute_query(query_add, params=params)
            execute_query(query_delete_watchlist, params=(movie_id,))
            return redirect(f'/{movie_id}')
        except Exception as e:
            print(e)
            error = "Une erreur est survenue lors de l'ajout du film à la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400

@app.route('/add_movie_watchlist', methods=['POST'])
def add_movie_watchlist():
    error = "Un erreur est survenue."
    if request.method == 'POST':
        movie_id = request.form.getlist('movie_add')[0]
        movie_info = get_movie_info(movie_id)
        movie_info['rating'] = movie_info['average_rating']
        if not movie_info:
            return jsonify({"error": "Film introuvable."}), 400
        columns = ("tmdb_id", "title", "poster", "year", "rating")
        placeholders = ", ".join(["?"] * len(columns))
        query = f"""
            INSERT into watchlist ({", ".join(columns)}) values({placeholders})
            ON CONFLICT(tmdb_id) 
            DO NOTHING
            ;
        """
        params = tuple(movie_info[c] for c in columns)
        try:
            execute_query(query, params=params)
            return redirect('/watchlist')
        except Exception as e:
            print(e)
            error = "Une erreur est survenue lors de l'ajout du film à la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400

    
@app.route('/search_movie', methods=['POST'])
def route_search_movie():
    error = "Un erreur est survenue."
    if request.method == 'POST':
        request_data = request.get_json()
        title = request_data.get('title')
        if not title:
            error = "Le titre du film est requis."
        else:
            search_results = search_movie(title)
            if not search_results:
                error = "Aucun résultat trouvé pour ce titre."
            else:
                return jsonify({"results": search_results})
    return jsonify({"error": error}), 400


@app.route('/update_movie/<int:tmdb_id>', methods=['POST', 'GET'])
def update_movie(tmdb_id):
    error = "Un erreur est survenue."
    if request.method == 'POST':
        movie_info = {}
        movie_info['rating'] = request.form.getlist('rating')[0]
        movie_info['summary'] = request.form.getlist('summary')[0]
        movie_info['date'] = request.form.getlist('date')[0]
        movie_info['review'] = request.form.getlist('review')[0]
        columns = ("rating", "date", "summary", "review")
        placeholders = ", ".join(["?"] * len(columns))
        query = f"""
            UPDATE movies
            SET {", ".join([f"{c} = ?" for c in columns])}
            WHERE tmdb_id = ?;
        """
        params = tuple(movie_info[c] for c in columns) + (tmdb_id,)
        try:
            execute_query(query, params=params)
            return redirect(f'/{tmdb_id}')
        except Exception as e:
            print(e)
            error = "Une erreur est survenue lors de la mise à jour du film dans la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400

@app.route('/delete_movie/<int:tmdb_id>', methods=['POST'])
def delete_movie(tmdb_id):
    error = "Un erreur est survenue."
    if request.method == 'POST':
        try:
            execute_query('DELETE FROM movies WHERE tmdb_id = ?', params=(tmdb_id,))
            return redirect('/')
        except Exception as e:
            print(e)
            error = "Une erreur est survenue lors de la suppression du film de la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400

@app.route('/delete_movie_watchlist/<int:tmdb_id>', methods=['POST'])
def delete_movie_watchlist(tmdb_id):
    error = "Un erreur est survenue."
    if request.method == 'POST':
        try:
            execute_query('DELETE FROM watchlist WHERE tmdb_id = ?', params=(tmdb_id,))
            return '', 204
        except Exception as e:
            print(e)
            error = "Une erreur est survenue lors de la suppression du film de la watchlist."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400
