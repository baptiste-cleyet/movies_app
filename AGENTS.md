# AGENTS.md — movies (Flask + SQLite + Vite)

## Stack & entrypoints
- `wsgi.py`: `create_app()` + module-level `app`/`application` (l'alias `application` est requis par uWSGI alwaysdata — ne pas le retirer).
- `config.py` lit l'env **à l'import** ; `app/movie_info_request.py` lit `TMDB_API_KEY` **paresseusement** (`_api_key()`, à chaque appel) — ne jamais revenir à une lecture au niveau module, ça cassait la prod (env pas encore chargé à l'import sous uWSGI).
- Frontend Vite+Tailwind → `static/dist/` (gitignoré). Rebuild obligatoire avant tout déploiement touchant CSS/JS **ou ajoutant des classes Tailwind dans les templates** (`npm run build`) — sinon les nouveaux utilitaires manquent dans le CSS compilé et la mise en page s'effondre. Exception : `static/css/login.css` est linké directement (pas besoin de build pour le modifier).

## Commandes
- Installer les outils de dev : `pip install -r requirements-dev.txt`.
- Tests : `python -m pytest -q` (~34; un seul test : `python -m pytest -q tests/test_auth.py::test_mobile_menu_overlay`). Lint : `ruff check .` (4 erreurs pré-existantes sur le baseline — ne pas les « corriger » au passage).
- Contexte tests (`tests/conftest.py`) : `SITE_PASSWORD="test-password"`, CSRF désactivé, fixture `client` **auto-authentifiée**, `anon_client` pour les cas non connectés.
- BDD locale : `flask db upgrade` (migrations via Flask-Migrate). Ne jamais committer `data/database.db`.

## Auth (globale, mot de passe unique)
- `app/auth.py` + `app/routes/auth.py` + `templates/login.html`. Garde `before_request` : pages → redirect `/login`, blueprint `api` → 401 JSON.
- `SITE_PASSWORD` requis : fail-fast en prod (`FLASK_ENV=production`), fallback dev avec warning. Hashé une fois par processus (PBKDF2).
- `WTF_CSRF_SSL_STRICT = False` (config) : derrière le reverse proxy alwaysdata, exiger le `Referer` casse les appels `fetch` légitimes. Ne pas réactiver.
- Rate limit login : 10 échecs / 10 min / IP → 429. `Cache-Control: no-store` sur HTML/JSON (tokens CSRF + contenu authentifié) ; statics intacts.

## Frontend (menu mobile)
- Menu mobile = pilule `#menu-icon` (top-right) + overlay plein écran `#mobile-ul` (`.mobile-overlay`, z-40 sous la pilule z-50). Fermeture : bouton `#menu-close`, clic fond/item, Échap, scroll bloqué (`body.overflow-hidden`). La bascule de thème (`*-mode-mobile` ferme PAS l'overlay intentionnellement). La page courante est marquée via `.current` (comparaison `pathname`).
- `.menu` (menu laptop, dégradé radial inversé par thème, dans base.css) : le texte sur menu doit être `--primary-color` (inversé vs le body). L'overlay mobile `.mobile-overlay` n'utilise PAS `.menu` : il est aligné sur les couleurs du corps via la permutation `--body-bg`/`--body-text` (capture inversion). Les icônes d'items doivent être enregistrées dans `static/js/icons.js` (les `<i data-lucide>` cachés sont remplacés quand même).
- Le menu (mobile + laptop) n'est rendu que si `menuItems` est non vide : la page de connexion (non authentifié) n'a pas de menu.
- Piège cascade : le CSS custom de `base.css` (après `@import "tailwindcss"`) est **non-layered**, il écrase TOUJOURS les utilitaires Tailwind (y compris `.hidden`). Donc état du menu via classe dédiée `.open` sur l'overlay (`display:none` par défaut), jamais via `.hidden`.

## Git (repo public : doit rester clonable par n'importe qui)
- Aucune info perso dans le code versionné : ni secrets, ni `user@host`, ni chemins locaux. `.env` jamais committé (historique vérifié propre). Secrets de test factices uniquement (`"test-password"`, `change-me`).
- `.coverage`, `data/database.db*`, WAL/journal déjà ignorés (.gitignore) — ne pas réindexer ces artefacts.
- La config perso du backup vit dans `.env` (clés `BACKUP_*`, gitignoré), jamais dans le code versionné.

## Déploiement alwaysdata (manuel, pas de CI/Docker sur le mutualisé)
- Toujours via `./deploy-alwaysdata.sh` (`--dry-run` d'abord ; `--migrate` si le schéma change). Il build le frontend, envoie **uniquement** une liste blanche de fichiers runtime (`app/ config.py wsgi.py migrations/ templates/ static/ requirements.txt`, `--delete` seulement à l'intérieur de ces dossiers), puis `pip install -r requirements.txt` + `pip check`. Hôte et dossier lus dans `.env` (`DEPLOY_SSH_HOST`, `DEPLOY_REMOTE_DIR`, voir `.env.example`).
- Ne jamais revenir à un rsync de `./` entier : les fichiers de dev (tests, Docker, docs, `.env`) se retrouvaient en prod, et un `--delete` global a déjà détruit le venv distant.
- Aucun `.env` sur le serveur : les secrets prod vivent dans **les variables d'env du site côté admin** (`FLASK_ENV`, `FLASK_SECRET_KEY`, `TMDB_API_KEY`, `TMDB_LANGUAGE`, `SITE_PASSWORD`).
- Origine des valeurs (pour recréer le site) : `TMDB_API_KEY` sur le compte TMDB (themoviedb.org > Paramètres > API) ; `SITE_PASSWORD` dans le gestionnaire de mots de passe ; `FLASK_SECRET_KEY` régénérable (`python -c "import secrets; print(secrets.token_hex(32))"`, seules les sessions sont invalidées) ; `FLASK_ENV=production`, `TMDB_LANGUAGE=fr-FR`.
- Dépendances : `requirements.txt` = prod uniquement (gunicorn inclus pour Docker) ; `requirements-dev.txt` = prod + pytest, pytest-cov, ruff (dev local). Ne pas remettre d'outils de dev dans `requirements.txt` : ils seraient installés dans le venv de prod.
- venv distant : `~/www/movies/venv`, Python 3.11 imposé (`python3.11 -m venv venv`) ; défaut du compte : 3.13.
- **Redémarrage manuel obligatoire** dans l'admin après chaque déploiement (uWSGI ne recharge pas seul). Debug : `~/admin/logs/uwsgi/[id].log`.
- Ne pas se fier à `curl`/`requests` sans précaution : les 302 suivies automatiquement masquent le garde d'auth ; tester avec `allow_redirects=False` et un param d'URL unique (évite tout cache).

## Backup prod
- Le backup est tiré **par le PC** (cron horaire), pas par le serveur, avec un script partagé entre projets **hors de ce repo** : backup à chaud distant via `sqlite3 .backup` + `scp`, `PRAGMA integrity_check`, nom journalier (écrasé dans la journée), une copie identique à la précédente la remplace, rétention 10 fichiers.
- Destination : `backups/` à la racine du projet (gitignoré). Journal : `backups/backup.log`.
- Config lue dans `.env` (parsée, jamais sourcée) : `BACKUP_SSH_HOST` (alias `~/.ssh/config`, clé dédiée sans passphrase), `BACKUP_REMOTE_DB` ; optionnels `BACKUP_DIR`, `BACKUP_KEEP`. Voir `.env.example`.
- Restauration : script partagé hors de ce repo (`--dry-run` d'abord ; sauvegarde la prod en `backups/pre-restore_*.db` avant ; charge via `sqlite3 <db> ".restore <fichier>"`, sans arrêter le site), puis redémarrer le site. Ne jamais copier un `.db` par-dessus la base vivante (WAL).
- `scripts/backup_db.sh` (documenté README, backup local 20h générique) n'est PAS celui utilisé sur l'infra réelle.

## Pièges `.env`
- Valeurs avec caractères spéciaux : quoter (surtout `SITE_PASSWORD`) — sinon `source .env` en bash casse ; dans les scripts, lire via `python -c "from dotenv import dotenv_values"`, jamais via `set -a; . .env`.
- Ne jamais afficher/copier les secrets dans les réponses ou les logs.
