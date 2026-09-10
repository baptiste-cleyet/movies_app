# Movies app

> A Flask application where you can save all the movies you've seen, with own summary and review. All public information comes from the TMDB API.

---

> Project by Baptiste Cleyet.
> For question or information contact [bcleyet@gmail.com](mailto:bcleyet@gmail.com).

# Setup

## Prerequisites

- Python 3.11+
- Node.js 20+ and npm
- A TMDB API key ([create account](https://www.themoviedb.org/signup) → [API settings](https://www.themoviedb.org/settings/api))

## Flask

### Installation

Clone the repository and create a virtual environment:

```bash
git clone <repo-url>
cd movies
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Visit the [Flask installation docs](https://flask.palletsprojects.com/en/stable/installation/) for details.

### Environment

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Required variables in `.env` (see `.env.example`):

```
TMDB_API_KEY=your_tmdb_api_key
FLASK_SECRET_KEY=change-me-in-production
# Optional: DATABASE_URL=sqlite:///data/database.db
# Optional: TMDB_LANGUAGE=fr-FR
```

`FLASK_SECRET_KEY` must be set in production (`FLASK_ENV=production` will fail fast if missing). For local dev a warning and dev fallback is used.

### Database

The database is managed via Flask-Migrate (Alembic). 

```bash
flask db upgrade
```

This creates `data/database.db` (gitignored, auto-created via `config.py`). To create a new migration after model changes:

```bash
flask db migrate -m "describe change"
flask db upgrade
```

Downgrade if needed: `flask db downgrade -1`

## Dependencies

### Python

All Python deps are pinned in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Includes `Flask`, `Flask-WTF`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Requests`, `gunicorn`, `python-dotenv`, `pytest`, `pytest-cov`, `ruff`.

[More information](https://pypi.org/project/python-dotenv/) for dotenv.
[More information](https://pypi.org/project/requests/) for requests.

### Frontend (Vite + Tailwind)

> ⚠️ You can skip this step if you don't need to modify the styles or JS of the application. For production, just run the build.

Install JS dependencies:

```bash
npm ci
```

This triggers `postinstall` to copy `lucide` icons to `static/js/vendor/lucide`.

- Development with HMR:

```bash
npm run dev
```

- Production build (outputs to `static/dist/` with manifest):

```bash
npm run build
```

In production the app serves CSS via Vite manifest (`static/dist/.vite/manifest.json` looked up by `wsgi.py:vite_asset()`). For local dev without a build, the fallback `static/css/tailwind.css` is used if `static/dist` is missing.

More info: [TailwindCSS](https://tailwindcss.com/docs/installation/tailwind-cli) and [Vite](https://vitejs.dev/).

## Running the App

### Local (Flask dev server)

```bash
flask run --port 8000
# or
python wsgi.py
```

Visit `http://localhost:8000`

### Production (Gunicorn)

```bash
gunicorn -w 2 --threads 4 -b 0.0.0.0:8000 wsgi:app
```

Docker handles the `flask db upgrade` automatically before Gunicorn starts (`Dockerfile`).

### Docker

```bash
docker compose up --build
```

App available at `http://localhost:8000`. Data persists in `./data:/app/data` volume. Healthcheck uses `curl -f http://localhost:8000/`.

## Tests

```bash
pytest -q
pytest --cov=app          # with coverage (70%+)
```

Tests use a temporary SQLite DB (`tests/conftest.py`), `WTF_CSRF_ENABLED=False`, and mocked TMDB calls (`tests/test_routes.py`, `tests/test_tmdb.py`).

Lint/format:

```bash
ruff check .
ruff format .
```

Configured in `pyproject.toml` (line-length 100, target `py311`).

## Backup

Daily backup at **20:00** via cron (keeps 30 most recent). The script `scripts/backup_db.sh` is generic — edit its two variables before use.

- **Source / Destination:** edit in `scripts/backup_db.sh`:
  ```bash
  DB_SOURCE="enter the path to your SQLite database file here"
  BACKUP_DIR="enter the path to your backup directory here (cloud storage is preferable)"
  ```
  The script creates the backup directory if needed, runs a hot backup via `sqlite3 "$DB_SOURCE" ".backup '$BACKUP_DIR/$BACKUP_NAME'"` (WAL-safe), and prunes to 30 files:
  ```bash
  BACKUP_NAME="backup_$(date +%F).db"
  find "$BACKUP_DIR" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | head -n -30 | cut -d' ' -f2- | xargs -d '\n' -r rm --
  ```
- **Cron (20h):**
  ```cron
  0 20 * * * /path/to/movies/scripts/backup_db.sh >> /tmp/movies_backup.log 2>&1
  ```
  Verify: `crontab -l | grep backup` and `ls -lt "$BACKUP_DIR" | head`

---

# File Tree

## Use

- **app:** Flask application (models, routes, TMDB requests)
- **migrations:** Alembic migrations (`flask db` commands)
- **static:** images, js and css files (Vite builds to `static/dist`)
- **templates:** html files, `base.html` is used in every page, `*_modals.html` are used for the modals of the page with the same name
- **data:** database file (gitignored, created via `flask db upgrade`)
- **scripts:** backup script (`backup_db.sh` cron at 20h)
- **tests:** pytest suite
- **wsgi.py:** application factory and entry point
- **vite.config.js:** Vite + Tailwind config

## Representation

**Generated:** 10/09/2026 16:00:00

```
├── 📁 app
│   ├── 🐍 extensions.py
│   ├── 🐍 menu.py
│   ├── 🐍 models.py
│   ├── 🐍 movie_info_request.py
│   └── 📁 routes
│       ├── 🐍 api.py
│       └── 🐍 main.py
├── 📁 data
│   └── 🗃️ database.db (gitignored, created via flask db upgrade)
├── 📁 scripts
│   └── 📄 backup_db.sh
├── 📁 migrations
│   ├── 📄 alembic.ini
│   ├── 🐍 env.py
│   └── 📁 versions
│       ├── 🐍 a109d0ae1db1_initial_with_constraints.py
│       └── 🐍 66dcc507dced_p1_hardening.py
├── 📁 static
│   ├── 📁 css
│   │   ├── 🎨 base.css
│   │   ├── 🎨 grid.css
│   │   └── 🎨 movie_detail.css
│   ├── 📁 images
│   │   └── 🖼️ icon.png
│   └── 📁 js
│       ├── 📄 base.js
│       ├── 📄 grid.js
│       ├── 📄 grid_controller.js
│       ├── 📄 movie_detail.js
│       ├── 📄 movie_grid.js
│       └── 📄 watchlist.js
├── 📁 templates
│   ├── 🌐 400.html
│   ├── 🌐 500.html
│   ├── 🌐 base.html
│   ├── 🌐 grid.html
│   ├── 🌐 grid_modals.html
│   ├── 🌐 movie_detail.html
│   ├── 🌐 movie_detail_modals.html
│   ├── 🌐 movie_grid.html
│   ├── 🌐 movie_grid_modals.html
│   ├── 🌐 watchlist.html
│   └── 🌐 watchlist_modals.html
├── 📁 tests
│   ├── 🐍 conftest.py
│   ├── 🐍 test_db.py
│   ├── 🐍 test_routes.py
│   └── 🐍 test_tmdb.py
├── ⚙️ .env.example
├── ⚙️ .gitignore
├── ⚙️ config.py
├── ⚙️ docker-compose.yml
├── ⚙️ Dockerfile
├── ⚙️ package.json
├── ⚙️ pyproject.toml
├── ⚙️ requirements.txt
├── ⚙️ vite.config.js
├── ⚙️ wsgi.py
└── 📝 README.md
```

---

_Generated by FileTree Pro Extension_
