import os
import json
import pathlib
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, url_for

# Charge le .env situé à côté de ce fichier (chemin absolu) : ne dépend pas
# du répertoire de travail, qui varie selon le mode de lancement
# (dev local, gunicorn, uWSGI alwaysdata). Les variables déjà définies
# (ex. admin alwaysdata) restent prioritaires.
load_dotenv(pathlib.Path(__file__).resolve().parent / ".env")

# Alerte précoce visible dans le log uWSGI si la clé TMDB manque
# (la recherche renverrait systématiquement « aucun résultat »).
if not os.getenv("TMDB_API_KEY"):
    import warnings

    warnings.warn(
        "TMDB_API_KEY is not set: la recherche de films ne renverra aucun résultat.",
        UserWarning,
    )
from flask_wtf.csrf import CSRFProtect  # noqa: E402 (après load_dotenv, voulu)
from app.auth import init_auth, register_guard  # noqa: E402
from app.extensions import db, migrate  # noqa: E402
from app.routes.main import bp as main_bp  # noqa: E402
from app.routes.api import bp as api_bp  # noqa: E402
from app.routes.auth import bp as auth_bp  # noqa: E402

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object("config")
    if test_config:
        app.config.update(test_config)

    # Fail fast if SECRET_KEY missing outside testing
    # In production (FLASK_ENV=production) missing key is an error; for local dev allow fallback with warning
    if not app.config.get("SECRET_KEY"):
        if app.config.get("TESTING"):
            app.config["SECRET_KEY"] = "test-secret-key-not-for-production"
        elif os.getenv("FLASK_ENV") == "production":
            raise RuntimeError(
                "FLASK_SECRET_KEY is not set. "
                "Set it in .env or environment (see .env.example)."
            )
        else:
            import warnings
            warnings.warn("FLASK_SECRET_KEY not set, using dev fallback. Set it for production.", UserWarning)
            app.config["SECRET_KEY"] = "dev-only-change-me"

    # SQLAlchemy
    db.init_app(app)
    migrate.init_app(app, db)

    csrf.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    # Session longue durée + cookie sécurisé en production (HTTPS).
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
        days=app.config.get("PERMANENT_SESSION_LIFETIME_DAYS", 30)
    )
    if os.getenv("FLASK_ENV") == "production":
        app.config["SESSION_COOKIE_SECURE"] = True

    # Protection globale par mot de passe (init après config).
    init_auth(app)
    register_guard(app)

    @app.after_request
    def no_cache_private(response):
        # Pages HTML (contiennent le token CSRF de session) et JSON d'API :
        # ne jamais mettre en cache (ni navigateur, ni cache mutualisé),
        # sinon jetons périmés et fuites de contenu authentifié.
        if response.content_type.startswith(("text/html", "application/json")):
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response

    # Vite manifest helper for CSS/JS assets (robust for Docker vs local)
    def vite_asset(entry):
        # Try both manifest locations (Vite 5/6 vs 8)
        candidates = [
            pathlib.Path(app.static_folder) / "dist" / ".vite" / "manifest.json",
            pathlib.Path(app.static_folder) / "dist" / "manifest.json",
        ]
        for manifest_path in candidates:
            try:
                if manifest_path.exists():
                    data = json.loads(manifest_path.read_text())
                    if entry in data:
                        return url_for("static", filename="dist/" + data[entry]["file"])
            except Exception:
                continue
        # Fallback: glob for style assets if manifest missing (e.g., Docker build mismatch)
        try:
            dist_assets = pathlib.Path(app.static_folder) / "dist" / "assets"
            if dist_assets.exists() and entry == "static/css/base.css":
                # find style-* or style.*.css
                for p in dist_assets.glob("style*.css"):
                    return url_for("static", filename=f"dist/assets/{p.name}")
        except Exception:
            pass
        return None

    @app.context_processor
    def inject_vite():
        return dict(vite_asset=vite_asset)

    @app.errorhandler(404)
    def not_found(e):
        from app.menu import DARK_MODE_ITEMS
        menuItems = [
            {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
            {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        ] + DARK_MODE_ITEMS
        return render_template("404.html", menuItems=menuItems), 404

    @app.errorhandler(400)
    def bad_request(e):
        from app.menu import DARK_MODE_ITEMS
        menuItems = [
            {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
            {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        ] + DARK_MODE_ITEMS
        # Return JSON for API requests, HTML for pages
        from flask import request, jsonify
        if request.path.startswith("/search_movie") or request.is_json or request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "Requête invalide."}), 400
        return render_template("400.html", menuItems=menuItems), 400

    @app.errorhandler(500)
    def internal_error(e):
        from app.menu import DARK_MODE_ITEMS
        menuItems = [
            {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
            {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        ] + DARK_MODE_ITEMS
        return render_template("500.html", menuItems=menuItems), 500

    return app


app = create_app()

# Alias requis par certains serveurs WSGI (dont uWSGI sur alwaysdata,
# qui cherche par défaut un callable nommé `application`).
application = app
