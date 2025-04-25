# Importation des modules nécessaires
import time                            # Pour les pauses (sleep) et timestamps
from database import get_connection   # Fonction personnalisée pour se connecter à la base SQLite
from tmdb_utils import fetch_popular_movies  # Fonction pour récupérer les films depuis TMDB
import sqlite3                        # Pour interagir avec SQLite
from datetime import datetime         # Pour afficher la date/heure de lancement du cron
import os                             # Pour vérifier l'existence des fichiers
import gzip                           # Pour compresser les fichiers
import shutil                         # Pour copier le contenu d'un fichier dans un autre

# ➤ Définition du chemin du fichier de log et de la taille maximale avant rotation
LOG_PATH = "/app/cron.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB

# ➤ Fonction pour compresser et archiver le fichier de log s’il devient trop lourd
def rotate_log():
    # Vérifie si le fichier existe et dépasse la taille maximale
    if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > MAX_LOG_SIZE:
        timestamp = time.strftime("%Y%m%d-%H%M%S")  # Génère un timestamp (ex: 20250424-1432)
        archived_log = f"/app/cron_{timestamp}.log.gz"  # Nom du fichier compressé

        # 🔽 Compression du log
        with open(LOG_PATH, 'rb') as f_in:
            with gzip.open(archived_log, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)  # Copie et compresse le contenu

        os.remove(LOG_PATH)  # Supprime l'ancien fichier non compressé
        print(f"🔄 Log file rotated and compressed as {archived_log}")

# ➤ Insère un film dans la base de données
def insert_movie(cursor, movie):
    try:
        cursor.execute("""
            INSERT INTO movies (id, title, overview, release_date, original_language, 
                                popularity, vote_average, vote_count, poster_path, is_manual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            movie["id"],
            movie["title"],
            movie.get("overview", ""),
            movie.get("release_date", ""),
            movie.get("original_language", ""),
            movie.get("popularity", 0),
            movie.get("vote_average", 0),
            movie.get("vote_count", 0),
            movie.get("poster_path", "")
        ))
        return 1  # ✅ Retourne 1 si l’insertion a réussi
    except sqlite3.IntegrityError:
        return 0  # ❌ Retourne 0 si le film existe déjà (clé primaire)

# ➤ Retourne le nombre total de films actuellement dans la base
def get_total_movies(cursor):
    cursor.execute("SELECT COUNT(*) FROM movies;")
    return cursor.fetchone()[0]

# ➤ Fonction principale pour insérer les films populaires jusqu'à atteindre un seuil
def insert_popular_movies(min_movies=900):
    conn = get_connection()      # Connexion à la base SQLite
    cursor = conn.cursor()

    print(f"🕒 Cron job triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 🧹 Supprimer uniquement les films insérés automatiquement (is_manual = 0)
    print("🗑️ Suppression des anciens films dans la base...")
    cursor.execute("DELETE FROM movies WHERE is_manual = 0;")
    conn.commit()

    current_total = get_total_movies(cursor)
    initial_total = current_total  # Sauvegarde du nombre de films avant insertion
    page = 1  # Pagination TMDB

    # Boucle tant que le nombre de films est inférieur au seuil requis
    while current_total < min_movies:
        print(f"📥 Page {page} - Total actuel : {current_total} films")
        movies = fetch_popular_movies(page)
        if not movies:
            print("⚠️ Aucune donnée reçue de TMDB, on stoppe.")
            break

        inserted_this_page = 0
        for movie in movies:
            inserted_this_page += insert_movie(cursor, movie)

        conn.commit()  # Sauvegarde dans la base
        current_total = get_total_movies(cursor)
        page += 1
        time.sleep(1)  # Pause d'1 seconde entre chaque appel API

        # Si aucun film nouveau n’a été inséré, cela veut dire que tous les films sont déjà présents
        if inserted_this_page == 0:
            print("ℹ️ Aucun nouveau film inséré sur cette page, probablement tous les films sont déjà là.")
            break

    # Fermeture de la connexion et affichage du résumé
    conn.close()
    inserted_total = current_total - initial_total
    print(f"✅ Insertion terminée : {current_total} films dans la base. ➕ {inserted_total} nouveaux films ajoutés lors de ce run.")
    print("--------------------------------------------------------")

# ➤ Exécution principale du script (appelé automatiquement par le cron)
if __name__ == "__main__":
    rotate_log()  # 🔄 Avant d’insérer les films, gérer la rotation du log si nécessaire
    insert_popular_movies(min_movies=1000)
