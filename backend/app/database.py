import os
import sqlite3

# Récupérer le chemin de la base depuis les variables d'environnement (DATABASE_PATH dans .env)
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/db_data/movies.db")

def get_connection():
    """Crée une connexion à la base SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def create_movies_table():
    """Crée la table 'movies' si elle n'existe pas."""
    conn = get_connection()
    cursor = conn.cursor()

    # Requête SQL pour créer la table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        overview TEXT,
        release_date TEXT,
        original_language TEXT,
        popularity REAL,
        vote_average REAL,
        vote_count INTEGER,
        poster_path TEXT,
        is_manual BOOLEAN DEFAULT 0,
        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
