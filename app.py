import os
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from modules.db import close_db
from modules.routes.main import bp as main_bp
from modules.routes.api import bp as api_bp

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    # Ensure SECRET_KEY is set
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.urandom(24).hex()

    csrf.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Exempt only search per user choice
    from modules.routes.api import route_search_movie

    csrf.exempt(route_search_movie)

    app.teardown_appcontext(close_db)

    @app.errorhandler(404)
    def not_found(e):
        from modules.menu import DARK_MODE_ITEMS

        menuItems = [
            {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
            {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        ] + DARK_MODE_ITEMS
        return render_template("404.html", menuItems=menuItems), 404

    @app.errorhandler(400)
    def bad_request(e):
        from modules.menu import DARK_MODE_ITEMS

        menuItems = [
            {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
            {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        ] + DARK_MODE_ITEMS
        return render_template("404.html", menuItems=menuItems), 400

    return app


app = create_app()
