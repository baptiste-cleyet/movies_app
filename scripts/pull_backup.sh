#!/bin/bash
# Sauvegarde d'une BDD SQLite hébergée (ex. alwaysdata) tirée par le PC vers
# un dossier local (idéalement synchronisé type cloud).
# - Backup à chaud côté serveur (sqlite3 .backup, WAL-safe), puis scp vers le PC.
# - Exécuté toutes les heures par cron, mais nom de fichier journalier :
#   les runs d'un même jour écrasent le même fichier.
# - Conservation : 10 fichiers les plus récents (= ~10 jours).
#
# Configuration via variables d'environnement, ex. :
#   export SSH_USER="monuser" SSH_HOST="ssh-moncompte.alwaysdata.net"
#   export REMOTE_DB="/home/moncompte/www/movies/data/database.db"
#   export BACKUP_DIR="$HOME/Cloud/Backups/movies"
#   export MOUNT_CHECK="$HOME/pCloudDrive"   # optionnel : refus d'écrire si non monté
set -euo pipefail

: "${SSH_USER:?Définis SSH_USER (utilisateur SSH distant)}"
: "${SSH_HOST:?Définis SSH_HOST (ex. ssh-moncompte.alwaysdata.net)}"
: "${REMOTE_DB:?Définis REMOTE_DB (chemin absolu de la BDD distante)}"
: "${BACKUP_DIR:?Définis BACKUP_DIR (dossier local de sauvegarde)}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_alwaysdata_movies}"
KEEP="${KEEP:-10}"

# Un point de montage a un périphérique différent de son parent (repli sans
# mountpoint : comparaison des numéros de périphérique via stat).
is_mountpoint() {
    if command -v mountpoint >/dev/null 2>&1; then
        mountpoint -q "$1"
    else
        [ "$(stat -c %d "$1" 2>/dev/null)" != "$(stat -c %d "$(dirname "$1")" 2>/dev/null)" ]
    fi
}

# 0a. Pré-contrôle optionnel : dossier cloud (ex. pCloud) monté avant d'écrire.
# Sinon sortie propre (code 0) : la sauvegarde attendra le prochain passage du
# cron au lieu de créer un dossier local fantôme ou de spammer le log d'erreurs.
if [ -n "${MOUNT_CHECK:-}" ] && ! is_mountpoint "$MOUNT_CHECK"; then
    echo "[$(date '+%F %T')] INFO : ${MOUNT_CHECK} non monté — sauvegarde ignorée, nouvelle tentative au prochain cron."
    exit 0
fi

DATE="$(date +%F)"
BACKUP_NAME="backup_${DATE}.db"
REMOTE_TMP="/tmp/movies_${BACKUP_NAME}"

echo "[$(date '+%F %T')] Début sauvegarde ${BACKUP_NAME}"

mkdir -p "$BACKUP_DIR"

# 0. Pré-contrôle : rien à sauvegarder tant que le site n'est pas déployé.
# Sortie propre (code 0) pour ne pas spammer le log cron d'erreurs.
if ! ssh -i "$SSH_KEY" -o BatchMode=yes "${SSH_USER}@${SSH_HOST}" "test -f '${REMOTE_DB}'" 2>/dev/null; then
  echo "[$(date '+%F %T')] INFO : base distante absente (${REMOTE_DB}), site pas encore déployé — rien à sauvegarder."
  exit 0
fi

# 1. Backup à chaud côté serveur (évite de copier le .db live en cours d'écriture)
ssh -i "$SSH_KEY" -o BatchMode=yes "${SSH_USER}@${SSH_HOST}" \
  "sqlite3 '${REMOTE_DB}' \".backup '${REMOTE_TMP}'\""

# 2. Récupération vers le dossier cloud (-p préserve la date)
scp -p -i "$SSH_KEY" -o BatchMode=yes \
  "${SSH_USER}@${SSH_HOST}:${REMOTE_TMP}" \
  "${BACKUP_DIR}/${BACKUP_NAME}"

# 3. Nettoyage du fichier temporaire distant
ssh -i "$SSH_KEY" -o BatchMode=yes "${SSH_USER}@${SSH_HOST}" "rm -f '${REMOTE_TMP}'"

# 4. Vérification d'intégrité du fichier récupéré
if ! sqlite3 "${BACKUP_DIR}/${BACKUP_NAME}" "PRAGMA integrity_check;" | grep -q "^ok$"; then
  echo "[$(date '+%F %T')] ERREUR : integrity_check KO sur ${BACKUP_DIR}/${BACKUP_NAME}" >&2
  exit 1
fi

# 5. Rotation : garde les KEEP fichiers backup_*.db les plus récents
# head -n -KEEP affiche tout sauf les KEEP dernières lignes (= les plus anciens à supprimer) ;
# si <= KEEP fichiers, rien n'est supprimé (xargs -r ne tourne pas à vide).
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'backup_*.db' -printf '%T@ %p\n' \
  | sort -n \
  | head -n -${KEEP} \
  | cut -d' ' -f2- \
  | xargs -d '\n' -r rm --

echo "[$(date '+%F %T')] OK : ${BACKUP_DIR}/${BACKUP_NAME} ($(du -h "${BACKUP_DIR}/${BACKUP_NAME}" | cut -f1))"
