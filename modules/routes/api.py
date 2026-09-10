from flask import Blueprint, request, jsonify, redirect, current_app
from modules.movie_info_request import get_movie_info, search_movie
from modules.db import get_db

bp = Blueprint("api", __name__)


def _validate_rating(value):
    if value is None or value == "":
        abort_msg = "Note requise"
        return None, abort_msg
    try:
        r = int(value)
    except (ValueError, TypeError):
        return None, "Note invalide"
    if not 0 <= r <= 100:
        return None, "Note doit être entre 0 et 100"
    return r, None


@bp.route("/add_movie", methods=["POST", "GET"])
def add_movie():
    error = "Une erreur est survenue."
    if request.method == "POST":
        movie_id = request.form.get("movie_add")
        if not movie_id:
            return jsonify({"error": "Film requis."}), 400
        try:
            movie_id_int = int(movie_id)
        except ValueError:
            return jsonify({"error": "ID film invalide."}), 400

        movie_info = get_movie_info(movie_id_int)
        if not movie_info:
            return jsonify({"error": "Film introuvable."}), 400

        rating_raw = request.form.get("rating", "")
        try:
            rating = int(rating_raw) if rating_raw != "" else None
        except ValueError:
            return jsonify({"error": "Note invalide."}), 400
        if rating is not None and not 0 <= rating <= 100:
            return jsonify({"error": "Note doit être entre 0 et 100."}), 400

        summary = (request.form.get("summary") or "")[:2000]
        date = request.form.get("date") or None
        review = (request.form.get("review") or "")[:2000]

        movie_info["rating"] = rating
        movie_info["summary"] = summary
        movie_info["date"] = date
        movie_info["review"] = review

        columns = ("tmdb_id", "title", "poster", "rating", "date", "year", "summary", "review", "director", "runtime", "average_rating", "banner")
        placeholders = ", ".join(["?"] * len(columns))
        update_clause = ", ".join([f"{c} = excluded.{c}" for c in columns[1:]])
        query_add = f"INSERT into movies ({', '.join(columns)}) values({placeholders}) ON CONFLICT(tmdb_id) DO UPDATE SET {update_clause};"
        params = tuple(movie_info[c] for c in columns)

        try:
            conn = get_db()
            conn.execute(query_add, params)
            # persist genres (already filled per user, but ensure up-to-date)
            for g in movie_info.get("genres", []):
                conn.execute("INSERT OR IGNORE INTO genres(tmdb_id, genre) VALUES (?, ?)", (movie_id_int, g))
            conn.execute("DELETE FROM watchlist WHERE tmdb_id = ?", (movie_id_int,))
            conn.commit()
            return redirect(f"/{movie_id_int}")
        except Exception as e:
            current_app.logger.exception("add_movie DB error")
            error = "Une erreur est survenue lors de l'ajout du film à la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400


@bp.route("/add_movie_watchlist", methods=["POST"])
def add_movie_watchlist():
    error = "Une erreur est survenue."
    if request.method == "POST":
        movie_id = request.form.get("movie_add")
        if not movie_id:
            return jsonify({"error": "Film requis."}), 400
        try:
            movie_id_int = int(movie_id)
        except ValueError:
            return jsonify({"error": "ID film invalide."}), 400

        movie_info = get_movie_info(movie_id_int)
        if not movie_info:
            return jsonify({"error": "Film introuvable."}), 400
        movie_info["rating"] = movie_info["average_rating"]
        columns = ("tmdb_id", "title", "poster", "year", "rating")
        placeholders = ", ".join(["?"] * len(columns))
        query = f"INSERT into watchlist ({', '.join(columns)}) values({placeholders}) ON CONFLICT(tmdb_id) DO NOTHING;"
        params = tuple(movie_info[c] for c in columns)
        try:
            conn = get_db()
            conn.execute(query, params)
            conn.commit()
            return redirect("/watchlist")
        except Exception as e:
            current_app.logger.exception("add_movie_watchlist DB error")
            error = "Une erreur est survenue lors de l'ajout du film à la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400


@bp.route("/search_movie", methods=["POST"])
def route_search_movie():
    error = "Une erreur est survenue."
    if request.method == "POST":
        request_data = request.get_json(silent=True) or {}
        title = request_data.get("title")
        if not title or not title.strip():
            error = "Le titre du film est requis."
        else:
            search_results = search_movie(title.strip())
            if not search_results:
                error = "Aucun résultat trouvé pour ce titre."
            else:
                return jsonify({"results": search_results})
    return jsonify({"error": error}), 400


@bp.route("/update_movie/<int:tmdb_id>", methods=["POST", "GET"])
def update_movie(tmdb_id):
    error = "Une erreur est survenue."
    if request.method == "POST":
        rating_raw = request.form.get("rating", "")
        try:
            rating = int(rating_raw) if rating_raw != "" else None
        except ValueError:
            return jsonify({"error": "Note invalide."}), 400
        if rating is not None and not 0 <= rating <= 100:
            return jsonify({"error": "Note doit être entre 0 et 100."}), 400
        summary = (request.form.get("summary") or "")[:2000]
        date = request.form.get("date") or None
        review = (request.form.get("review") or "")[:2000]
        columns = ("rating", "date", "summary", "review")
        vals = {"rating": rating, "date": date, "summary": summary, "review": review}
        query = f"UPDATE movies SET {', '.join([f'{c} = ?' for c in columns])} WHERE tmdb_id = ?;"
        params = tuple(vals[c] for c in columns) + (tmdb_id,)
        try:
            conn = get_db()
            conn.execute(query, params)
            conn.commit()
            return redirect(f"/{tmdb_id}")
        except Exception as e:
            current_app.logger.exception("update_movie DB error")
            error = "Une erreur est survenue lors de la mise à jour du film dans la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400


@bp.route("/delete_movie/<int:tmdb_id>", methods=["POST"])
def delete_movie(tmdb_id):
    error = "Une erreur est survenue."
    if request.method == "POST":
        try:
            conn = get_db()
            conn.execute("DELETE FROM movies WHERE tmdb_id = ?", (tmdb_id,))
            conn.commit()
            return redirect("/")
        except Exception as e:
            current_app.logger.exception("delete_movie DB error")
            error = "Une erreur est survenue lors de la suppression du film de la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400


@bp.route("/delete_movie_watchlist/<int:tmdb_id>", methods=["POST"])
def delete_movie_watchlist(tmdb_id):
    error = "Une erreur est survenue."
    if request.method == "POST":
        try:
            conn = get_db()
            conn.execute("DELETE FROM watchlist WHERE tmdb_id = ?", (tmdb_id,))
            conn.commit()
            return "", 204
        except Exception as e:
            current_app.logger.exception("delete_movie_watchlist DB error")
            error = "Une erreur est survenue lors de la suppression du film de la watchlist."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400
