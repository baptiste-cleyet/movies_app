import os
import json
import pathlib
from flask import Flask, render_template, url_for
from flask_wtf.csrf import CSRFProtect
from app.extensions import db, migrate
from app.routes.main import bp as main_bp
from app.routes.api import bp as api_bp

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
