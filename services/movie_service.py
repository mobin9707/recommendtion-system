
from difflib import get_close_matches

from utils.text_utils import normalize_name


def find_movie(movies, movie_name):
    """
    جست‌وجوی فیلم بر اساس نام.
    این تابع ورودی را از کاربر نمی‌گیرد و چیزی چاپ نمی‌کند.
    """
    if not movie_name or not str(movie_name).strip():
        return {
            "status": "empty",
            "movie_index": None,
            "matches": []
        }

    normalized_name = normalize_name(movie_name)

    normalized_names = movies["name"].apply(normalize_name)

    # ابتدا دنبال تطبیق دقیق می‌گردیم.
    exact_matches = movies.index[
        normalized_names == normalized_name
    ].tolist()

    if exact_matches:
        return {
            "status": "found",
            "movie_index": exact_matches[0],
            "matches": exact_matches
        }

    # اگر تطبیق دقیق نبود، نزدیک‌ترین نام‌ها را پیدا می‌کنیم.
    unique_names = normalized_names.drop_duplicates().tolist()

    close_names = get_close_matches(
        normalized_name,
        unique_names,
        n=5,
        cutoff=0.5
    )

    suggested_indices = []

    for close_name in close_names:
        indices = movies.index[
            normalized_names == close_name
        ].tolist()

        suggested_indices.extend(indices)

    return {
        "status": "not_found",
        "movie_index": None,
        "matches": suggested_indices
    }
