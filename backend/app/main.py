from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from database import get_connection  # ➡️ Pour accéder à la base SQLite
from tmdb_utils import fetch_popular_movies


app = FastAPI()

# ✅ Modèle Pydantic pour la validation des données envoyées dans la requête
class Movie(BaseModel):
    id: int
    title: str
    overview: str = ""
    release_date: str = ""
    original_language: str = ""
    popularity: float = 0
    vote_average: float = 0
    vote_count: int = 0
    poster_path: str = ""

# 🎯 Endpoint de test pour vérifier que l'API tourne
@app.get("/")
async def root():
    return JSONResponse(content={"message": "🚀 Movie recommender backend is running!"})

# 🎬 Tester si l'accès à TMDB fonctionne
@app.get("/test-tmdb")
async def test_tmdb():
    movies = fetch_popular_movies(page=1)
    return {"movies": movies[:5]}  # On renvoie juste les 5 premiers pour tester

# 🔎 Rechercher des films par titre
@app.get("/search")
async def search_movies(query: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM movies 
        WHERE title LIKE ?
        ORDER BY popularity DESC
    """, (f"%{query}%",))
    results = cursor.fetchall()
    conn.close()
    return {"results": results}

# 📆 Filtrer les films par date de sortie
@app.get("/filter-by-date")
async def filter_by_date(from_date: str, to_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM movies 
        WHERE release_date BETWEEN ? AND ?
        ORDER BY release_date DESC
    """, (from_date, to_date))
    results = cursor.fetchall()
    conn.close()
    return {"results": results}

# 🔢 Trier les films par popularité, vote, etc.
@app.get("/sort")
async def sort_movies(by: str = "popularity", order: str = "desc"):
    valid_columns = ["popularity", "vote_average", "vote_count"]
    if by not in valid_columns:
        return {"error": "Invalid sorting column"}

    order = order.upper() if order.lower() in ["asc", "desc"] else "DESC"
    conn = get_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM movies ORDER BY {by} {order}"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return {"results": results}

@app.get("/movies")
async def get_movies(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    """
    📂 Récupère les films avec pagination + informations sur le total, la page suivante et précédente.
    - `page` : numéro de la page (par défaut 1)
    - `page_size` : nombre de films par page (par défaut 10, max 100)
    """

    offset = (page - 1) * page_size
    conn = get_connection()
    cursor = conn.cursor()

    # 🔢 Compter le nombre total de films
    cursor.execute("SELECT COUNT(*) FROM movies;")
    total_movies = cursor.fetchone()[0]

    # 📥 Récupérer les films avec limite et offset (pagination)
    cursor.execute("""
        SELECT id, title, overview, release_date, original_language, 
               popularity, vote_average, vote_count, poster_path, is_manual
        FROM movies
        ORDER BY popularity DESC
        LIMIT ? OFFSET ?
    """, (page_size, offset))

    results = cursor.fetchall()
    conn.close()

    movies = [
        {
            "id": row[0],
            "title": row[1],
            "overview": row[2],
            "release_date": row[3],
            "original_language": row[4],
            "popularity": row[5],
            "vote_average": row[6],
            "vote_count": row[7],
            "poster_path": row[8],
            "is_manual": bool(row[9]),
        }
        for row in results
    ]

    # 🔁 Calcul des pages suivantes et précédentes
    total_pages = (total_movies + page_size - 1) // page_size  # arrondi supérieur
    next_page = page + 1 if page < total_pages else None
    previous_page = page - 1 if page > 1 else None

    return {
        "page": page,
        "page_size": page_size,
        "total_movies": total_movies,
        "total_pages": total_pages,
        "next_page": next_page,
        "previous_page": previous_page,
        "movies": movies
    }


# 🆕 Endpoint pour ajouter un film manuellement
@app.post("/add-movie")
async def add_movie(movie: Movie):
    conn = get_connection()
    cursor = conn.cursor()

    # 🛑 Vérifier si le film existe déjà
    cursor.execute("SELECT id FROM movies WHERE id = ?", (movie.id,))
    existing_movie = cursor.fetchone()

    if existing_movie:
        conn.close()
        raise HTTPException(status_code=400, detail="Movie already exists in the database.")

    # ➕ Insertion dans la base avec is_manual = 1
    try:
        cursor.execute("""
            INSERT INTO movies (id, title, overview, release_date, original_language, 
                                popularity, vote_average, vote_count, poster_path, is_manual)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            movie.id,
            movie.title,
            movie.overview,
            movie.release_date,
            movie.original_language,
            movie.popularity,
            movie.vote_average,
            movie.vote_count,
            movie.poster_path
        ))
        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    conn.close()
    return {"message": f"✅ Movie '{movie.title}' inserted successfully with ID {movie.id}."}