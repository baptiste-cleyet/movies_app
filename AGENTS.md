# AGENTS.md — movies (Flask + SQLite + Vite)

## Stack & entrypoints
- `wsgi.py`: `create_app()` + module-level `app`/`application` (l'alias `application` est requis par uWSGI alwaysdata — ne pas le retirer).
- `config.py` lit l'env **à l'import** ; `app/movie_info_request.py` lit `TMDB_API_KEY` **paresseusement** (`_api_key()`, à chaque appel) — ne jamais revenir à une lecture au niveau module, ça cassait la prod (env pas encore chargé à l'import sous uWSGI).
- Frontend Vite+Tailwind → `static/dist/` (gitignoré). Rebuild obligatoire avant tout déploiement touchant CSS/JS **ou ajoutant des classes Tailwind dans les templates** (`npm run build`) — sinon les nouveaux utilitaires manquent dans le CSS compilé et la mise en page s'effondre.

## Commandes
- Tests : `python -m pytest -q` (26 tests). Lint : `ruff check .` (4 erreurs pré-existantes sur le baseline — ne pas les « corriger » au passage).
- Contexte tests (`tests/conftest.py`) : `SITE_PASSWORD="test-password"`, CSRF désactivé, fixture `client` **auto-authentifiée**, `anon_client` pour les cas non connectés.
- BDD locale : `flask db upgrade` (migrations via Flask-Migrate). Ne jamais committer `data/database.db`.

## Auth (globale, mot de passe unique)
- `app/auth.py` + `app/routes/auth.py` + `templates/login.html`. Garde `before_request` : pages → redirect `/login`, blueprint `api` → 401 JSON.
- `SITE_PASSWORD` requis : fail-fast en prod (`FLASK_ENV=production`), fallback dev avec warning. Hashé une fois par processus (PBKDF2).
- `WTF_CSRF_SSL_STRICT = False` (config) : derrière le reverse proxy alwaysdata, exiger le `Referer` casse les appels `fetch` légitimes. Ne pas réactiver.
- Rate limit login : 10 échecs / 10 min / IP → 429. `Cache-Control: no-store` sur HTML/JSON (tokens CSRF + contenu authentifié) ; statics intacts.

## Déploiement alwaysdata (manuel, pas de CI/Docker sur le mutualisé)
- Transfert par rsync vers `~/www/movies/`. Commande sûre (ne jamais `--delete` sans exclure le venv — ça a déjà détruit le venv distant une fois). Adapter `[compte]` à ton compte alwaysdata :
  `rsync -az -e "ssh -i ~/.ssh/id_alwaysdata_movies -o BatchMode=yes" --exclude='venv/' --exclude='.venv/' --exclude='node_modules/' --exclude='__pycache__/' --exclude='*.pyc' --exclude='.git/' --exclude='.env' --exclude='.pytest_cache/' --exclude='.coverage' --exclude='data/database.db*' --exclude='.directory' ./ [user]@ssh-[compte].alwaysdata.net:/home/[compte]/www/movies/`
- Ne jamais transférer `.env` (sauf procédure explicite) ; les secrets prod vivent dans **les variables d'env du site côté admin**, prioritaires sur le `.env`.
- venv distant : `~/www/movies/venv`, Python imposé via `PYTHON_VERSION=3.11 python -m venv` (défaut serveur : 3.14).
- **Redémarrage manuel obligatoire** dans l'admin après chaque déploiement (uWSGI ne recharge pas seul). Debug : `~/admin/logs/uwsgi/[id].log`.
- Ne pas se fier à `curl`/`requests` sans précaution : les 302 suivies automatiquement masquent le garde d'auth ; tester avec `allow_redirects=False` et un param d'URL unique (évite tout cache).

## Backup prod
- `scripts/pull_backup.sh` tourne **sur le PC** (cron horaire `0 * * * * ... >> /tmp/movies_backup_pull.log 2>&1`), pas sur le serveur : backup à chaud distant via `sqlite3 .backup` + `scp` vers pCloud. Nom journalier (écrasé dans la journée), rétention 10 fichiers.
- Clé dédiée sans passphrase : `~/.ssh/id_alwaysdata_movies`. Le script sort en code 0 avec un message INFO si la BDD distante est absente (site pas déployé).
- `scripts/backup_db.sh` et `~/.local/bin/backup_movies.sh` sont obsolètes (logique locale).

## Pièges `.env`
- Valeurs avec caractères spéciaux : quoter (surtout `SITE_PASSWORD`) — sinon `source .env` en bash casse ; dans les scripts, lire via `python -c "from dotenv import dotenv_values"`, jamais via `set -a; . .env`.
- Ne jamais afficher/copier les secrets dans les réponses ou les logs.
