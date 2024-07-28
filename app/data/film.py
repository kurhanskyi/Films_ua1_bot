import os
import json

def get_films(f_path: str = None) -> list:
    if f_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
        f_path = os.path.join(base_path, 'films.json')

    with open(f_path) as file:
        data = json.load(file)
        films = data.get('films')
        return films


def get_film(id: int = 0, f_path : str = None) -> dict:
    films = get_films(f_path)
    return films[id]

def save_film(film: dict = {}, f_path:str = None) -> bool:
    if f_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
        f_path = os.path.join(base_path, "films.json")

    with open(f_path, 'r') as f:
        data = json.load(f)
        films = data.get('films')
        films.append(film)

    with open(f_path, 'w') as f:
        json.dump(data, f, indent = 4)

def delete_film(title: str, f_path: str = None) -> bool:
    if f_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
        f_path = os.path.join(base_path, "films.json")

    films = get_films(f_path)
    film_to_delete = None

    for film in films:
        if title == film.get('title'):
            film_to_delete = film
            break

    if film_to_delete:
        films.remove(film_to_delete)

        with open(f_path, 'w') as write_file:
            json.dump({'films':films}, write_file, indent=4)
        return True
    return False

def update_film(title: str, updated_film: dict, f_path: str = None) -> bool:
    if f_path is None:
        base_path = os.path.dirname(os.path.abspath(__file__))
        f_path = os.path.join(base_path, "films.json")

    films = get_films(f_path)
    film_to_update = None

    for index, film in enumerate(films):
        if title == film.get('title'):
            film_to_update = index
            break

    if film_to_update is not None:
        films[film_to_update] = updated_film

        with open(f_path, 'w') as write_file:
            json.dump({'films': films}, write_file, indent=4)
        return True
    return False




def search_films(query: str, f_path: str = None) -> list:
    films = get_films(f_path)
    query = query.lower()
    matched_films = []
    for film in films:
        title = film.get('title', '').lower()
        if query in title:
            matched_films.append(film)
    return matched_filmss

