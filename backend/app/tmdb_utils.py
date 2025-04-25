import os
import requests

def fetch_popular_movies(page=1):
    """Récupère les films populaires depuis TMDB (par page)."""
    TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()  # <-- récupère à CHAQUE appel

    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY is not set!")

    url = "https://api.themoviedb.org/3/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": page
    }
    headers = {
        "User-Agent": "movie-recommender-app/1.0"
    }

    response = requests.get(url, params=params, headers=headers)
    
    print(response.status_code)
    print(response.text)

    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Erreur TMDB: {response.status_code} - {response.text}")
        return []
