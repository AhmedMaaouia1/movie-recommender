from database import get_connection

def list_movies(limit=10):
    """Affiche les N premiers films de la base."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, release_date FROM movies LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    print(f"📋 Liste des {limit} premiers films dans la base :")
    for row in rows:
        print(f"ID: {row[0]} | Titre: {row[1]} | Date de sortie: {row[2]}")

    conn.close()


def count_movies():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM movies;")
    count = cursor.fetchone()[0]
    print(f"🎬 Nombre total de films dans la base : {count}")

    conn.close()

if __name__ == "__main__":
    count_movies()
    #list_movies()