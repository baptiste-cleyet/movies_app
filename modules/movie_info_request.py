import requests
import os

API_KEY = os.getenv("TMDB_API_KEY")

def get_API_movie_details(movie_id):
    """Get the movie details from TMDB API

    Args:
        movie_id (int): The TMDB ID of the movie

    Returns:
        dict: The movie details
    """
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": API_KEY, "language": "fr-FR"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def director(tmdb_id):
    """Get the director of a movie

    Args:
        tmdb_id (int): The TMDB ID of the movie

    Returns:
        str: The name of the director
    """
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits"
    params = {"api_key": API_KEY, "language": "fr-FR"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    credits = response.json()

    for member in credits.get("crew", []):
        if member.get("job") == "Director":
            return member.get("name")
    return None

def runtime(movie_id) :
    """Get the runtime of a movie

    Args:
        movie_id (int): The TMDB ID of the movie

    Returns:
        str: The runtime of the movie in the format "Xh Ymin"
    """
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    runtime = requests.get(url).json().get('runtime')
    return f"{runtime//60}h {runtime%60}" if runtime else None

def genres(movie_id) :
    """Get the genres of a movie

    Args:
        movie_id (int): The TMDB ID of the movie

    Returns:
        list: The list of genres
    """
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    return [g['name'] for g in requests.get(url).json().get('genres', [])]

def average_rating(movie_id) :
    """Get the average rating of a movie

    Args:
        movie_id (int): The TMDB ID of the movie

    Returns:
        float: The average rating of the movie
    """
    note = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}').json().get('vote_average')
    return round(note, 1) * 10






def search_movie(title):
    """Search a movie in the API from its title

    Args:
        title (str): The title of the movie

    Returns:
        list: The list of the 3 first movies matching the title
    """
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "language": "fr-FR",
        "include_adult": False,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    resultats = response.json()

    if resultats["results"]:
        return resultats["results"][:3]
    return None




def get_movie_info(movie_id):
    """Get the movie info from TMDB API

    Args:
        movie_id (int): The TMDB ID of the movie

    Returns:
        dict: The movie info
    """

    film = get_API_movie_details(movie_id)
    if not film :
        print("❌ Movie not found.")
        return None

    info = {
        "title": film.get("title") if film.get("title") else None,
        "poster": "https://image.tmdb.org/t/p/w500" + film.get("poster_path") if film.get("poster_path") else None,
        "banner": "https://image.tmdb.org/t/p/w1280" + film.get("backdrop_path") if film.get("backdrop_path") else None,
        "tmdb_id": movie_id,
        "average_rating": average_rating(movie_id),
        "year": film.get("release_date").split('-')[0] if film.get("release_date") else None,
        "director": director(movie_id),
        "runtime": runtime(movie_id),
        "genres": genres(movie_id),
    }

    return info