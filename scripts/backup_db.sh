DB_SOURCE="enter the path to your SQLite database file here"
BACKUP_DIR="enter the path to your backup directory here (cloud storage is preferable)"

# Créer le dossier de backup s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Nom du fichier avec la date du jour (ex: backup_2026-06-10.db)
BACKUP_NAME="backup_$(date +%F).db"

# Exécution de la sauvegarde à chaud via sqlite3
sqlite3 "$DB_SOURCE" ".backup '$BACKUP_DIR/$BACKUP_NAME'"

# Suppression des sauvegardes les plus anciennes si le nombre de fichiers dépasse 30
find "$BACKUP_DIR" -maxdepth 1 -type f -printf '%T@ %p\n' | sort -n | head -n -30 | cut -d' ' -f2- | xargs -d '\n' -r rm --