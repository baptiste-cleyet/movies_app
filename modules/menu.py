DARK_MODE_ITEMS = [
    {"id": "dark-mode", "name": "Sombre", "iconName": "moon"},
    {"id": "light-mode", "name": "Clair", "iconName": "sun"},
]

SORT_ITEMS_MOVIES = [
    {"id": "date-sort", "name": "Date de visionnage", "iconName": "calendar"},
    {"id": "title-sort", "name": "Titre", "iconName": "type"},
    {"id": "rating-sort", "name": "Note", "iconName": "star"},
    {"id": "year-sort", "name": "Année de sortie", "iconName": "calendar-clock"},
]

SORT_ITEMS_WATCHLIST = [
    {"id": "title-sort", "name": "Titre", "iconName": "type"},
    {"id": "rating-sort", "name": "Note", "iconName": "star"},
    {"id": "year-sort", "name": "Année de sortie", "iconName": "calendar-clock"},
]


def get_menu_items(page):
    base = {
        "index": [
            {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
            {"id": "search-button", "name": "Rechercher", "iconName": "search"},
            {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
            {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
        ],
        "watchlist": [
            {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
            {"id": "search-button", "name": "Rechercher", "iconName": "search"},
            {"id": "sort-button", "name": "Trier", "iconName": "arrow-down-wide-narrow"},
            {"id": "add-button", "name": "Ajouter", "iconName": "file-plus-2"},
        ],
        "detail": lambda tmdb_id: [
            {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
            {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
            {"id": "delete-movie-button", "name": "Supprimer", "iconName": "trash-2"},
            {"id": "update-movie-button", "name": "Mettre à jour", "iconName": "pencil"},
            {"id": "tmdb-link", "name": "Page TMDB", "iconName": "square-arrow-out-up-right", "href": f"https://www.themoviedb.org/movie/{tmdb_id}", "mobileOnly": True},
        ],
    }
    items = base[page]
    if callable(items):
        items = items
    # Handle detail callable case
    if page == "detail":
        # caller will pass tmdb_id via get_detail_menu
        return base["detail"]
    return items + DARK_MODE_ITEMS


def get_detail_menu(tmdb_id):
    return [
        {"id": "movie-grid-button", "name": "Grille de films", "iconName": "layout-grid", "href": "/"},
        {"id": "watchlist-button", "name": "Watchlist", "iconName": "eye", "href": "/watchlist"},
        {"id": "delete-movie-button", "name": "Supprimer", "iconName": "trash-2"},
        {"id": "update-movie-button", "name": "Mettre à jour", "iconName": "pencil"},
        {"id": "tmdb-link", "name": "Page TMDB", "iconName": "square-arrow-out-up-right", "href": f"https://www.themoviedb.org/movie/{tmdb_id}", "mobileOnly": True},
    ] + DARK_MODE_ITEMS
