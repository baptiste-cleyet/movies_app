from flask import Blueprint, request, jsonify, redirect, current_app
from app.movie_info_request import get_movie_info, search_movie
from app.extensions import db
from app.models import Movie, Genre, Watchlist
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

bp = Blueprint("api", __name__)


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

        try:
            movie = Movie.query.get(movie_id_int)
            if movie:
                for col in ("title", "poster", "rating", "date", "year", "summary", "review", "director", "runtime", "average_rating", "banner"):
                    setattr(movie, col, movie_info[col])
            else:
                movie = Movie(
                    tmdb_id=movie_id_int,
                    title=movie_info["title"],
                    poster=movie_info["poster"],
                    rating=movie_info["rating"],
                    date=movie_info["date"],
                    year=int(movie_info["year"]) if movie_info["year"] else None,
                    summary=movie_info["summary"],
                    review=movie_info["review"],
                    director=movie_info["director"],
                    runtime=movie_info["runtime"],
                    average_rating=movie_info["average_rating"],
                    banner=movie_info["banner"],
                )
                db.session.add(movie)
            db.session.flush()
            # sync genres
            existing = {g.genre for g in movie.genres}
            for g in movie_info.get("genres", []):
                if g not in existing:
                    db.session.add(Genre(tmdb_id=movie_id_int, genre=g))
            # remove from watchlist
            wl = Watchlist.query.get(movie_id_int)
            if wl:
                db.session.delete(wl)
            db.session.commit()
            return redirect(f"/{movie_id_int}")
        except Exception:
            db.session.rollback()
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

        try:
            if Watchlist.query.get(movie_id_int):
                return redirect("/watchlist")
            wl = Watchlist(
                tmdb_id=movie_id_int,
                title=movie_info["title"],
                poster=movie_info["poster"],
                year=int(movie_info["year"]) if movie_info["year"] else 0,
                rating=movie_info["average_rating"] or 0,
            )
            db.session.add(wl)
            db.session.commit()
            return redirect("/watchlist")
        except Exception:
            db.session.rollback()
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
        try:
            movie = Movie.query.get(tmdb_id)
            if not movie:
                return jsonify({"error": "Film introuvable."}), 404
            movie.rating = rating
            movie.date = date
            movie.summary = summary
            movie.review = review
            db.session.commit()
            return redirect(f"/{tmdb_id}")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("update_movie DB error")
            error = "Une erreur est survenue lors de la mise à jour du film dans la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400


@bp.route("/delete_movie/<int:tmdb_id>", methods=["POST"])
def delete_movie(tmdb_id):
    error = "Une erreur est survenue."
    if request.method == "POST":
        try:
            movie = Movie.query.get(tmdb_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
            return redirect("/")
        except Exception:
            db.session.rollback()
            current_app.logger.exception("delete_movie DB error")
            error = "Une erreur est survenue lors de la suppression du film de la base de données."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400


@bp.route("/delete_movie_watchlist/<int:tmdb_id>", methods=["POST"])
def delete_movie_watchlist(tmdb_id):
    error = "Une erreur est survenue."
    if request.method == "POST":
        try:
            wl = Watchlist.query.get(tmdb_id)
            if wl:
                db.session.delete(wl)
                db.session.commit()
            return "", 204
        except Exception:
            db.session.rollback()
            current_app.logger.exception("delete_movie_watchlist DB error")
            error = "Une erreur est survenue lors de la suppression du film de la watchlist."
            return jsonify({"error": error}), 400
    return jsonify({"error": error}), 400
