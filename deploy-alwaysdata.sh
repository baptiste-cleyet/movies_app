#!/usr/bin/env bash
# Deploy the movies app to alwaysdata (shared hosting, uWSGI, no Docker).
#
# Usage:
#   ./deploy-alwaysdata.sh             # build frontend, sync runtime files, install deps
#   ./deploy-alwaysdata.sh --dry-run   # show what would be transferred, change nothing
#   ./deploy-alwaysdata.sh --migrate   # same as default + `flask db upgrade` on the server
#
# Only the runtime files are sent (whitelist): app/ config.py wsgi.py migrations/
# templates/ static/ requirements.txt. The server's venv/, data/ and any .env are never
# touched. Restart the site in the alwaysdata panel afterwards (uWSGI does not reload).
#
# Configuration (read from .env, parsed, never sourced; no personal value in this repo):
#   DEPLOY_SSH_HOST     SSH destination, e.g. a ~/.ssh/config alias (key auth)
#   DEPLOY_REMOTE_DIR   app directory on the server, e.g. /home/<account>/www/movies
set -Eeuo pipefail
cd "$(dirname "$0")"

DRY_RUN=false
MIGRATE=false
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --migrate) MIGRATE=true ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done

# Value of KEY from .env, dotenv-style (quotes, inline " # comments", last one wins).
env_value() {
    local line
    line="$(grep -E "^[[:space:]]*(export[[:space:]]+)?$1=" .env 2>/dev/null | tail -n 1 || true)"
    line="${line#*=}"
    line="${line%$'\r'}"
    line="${line#"${line%%[![:space:]]*}"}"
    if [[ "$line" =~ ^\"([^\"]*)\" || "$line" =~ ^\'([^\']*)\' ]]; then
        line="${BASH_REMATCH[1]}"
    else
        [[ "$line" == \#* ]] && line=""
        line="$(printf '%s' "$line" | sed -E 's/[[:space:]]+#.*$//; s/[[:space:]]+$//')"
    fi
    printf '%s' "$line"
}

HOST="$(env_value DEPLOY_SSH_HOST)"
DIR="$(env_value DEPLOY_REMOTE_DIR)"
[ -n "$HOST" ] || { echo "DEPLOY_SSH_HOST missing in .env" >&2; exit 1; }
[ -n "$DIR" ]  || { echo "DEPLOY_REMOTE_DIR missing in .env" >&2; exit 1; }

# One multiplexed SSH connection: alwaysdata resets bursts of new connections.
CTL_DIR="$(mktemp -d)"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=20
          -o ControlMaster=auto -o "ControlPath=$CTL_DIR/cm" -o ControlPersist=60)
cleanup() {
    ssh -o "ControlPath=$CTL_DIR/cm" -O exit "$HOST" 2>/dev/null || true
    rm -rf "$CTL_DIR"
}
trap cleanup EXIT
remote() { ssh "${SSH_OPTS[@]}" "$HOST" "$@"; }

RSYNC=(rsync -az --itemize-changes -e "ssh ${SSH_OPTS[*]}" --exclude='__pycache__/' --exclude='*.pyc')
$DRY_RUN && RSYNC+=(--dry-run)

echo "==> Check remote app directory"
remote "test -d '$DIR/venv'" || { echo "No venv in $DIR on $HOST: wrong DEPLOY_REMOTE_DIR?" >&2; exit 1; }

if $DRY_RUN; then
    echo "==> Dry run: frontend build skipped (static/dist compared as it is locally)"
else
    echo "==> Build frontend"
    npm run build
fi

echo "==> Sync runtime files to $HOST:$DIR"
# Directories: mirrored (--delete only acts inside each of them).
for d in app migrations templates static; do
    "${RSYNC[@]}" --delete "$d/" "$HOST:$DIR/$d/"
done
"${RSYNC[@]}" config.py wsgi.py requirements.txt "$HOST:$DIR/"

if $DRY_RUN; then
    echo "==> Dry run: nothing changed on the server."
    exit 0
fi

echo "==> Python dependencies"
remote "cd '$DIR' && venv/bin/pip install -q -r requirements.txt && venv/bin/pip check"

if $MIGRATE; then
    echo "==> Database migrations"
    remote "cd '$DIR' && venv/bin/flask --app wsgi db upgrade"
fi

echo
echo "Done. Next: alwaysdata panel > Web > Sites > restart the site, then check it."
$MIGRATE || echo "Schema changed? Re-run with --migrate (back up the database first)."
