
import pandas as pd
import pytest
from services.movie_service import find_movie


@pytest.fixture
def movies():
    return pd.DataFrame(
        {
            "name": [
                "Avatar",
                "Titanic",
                "The Matrix",
                "Avatar",
            ]
        }
    )


def test_find_movie_exact_match(movies):
    result = find_movie(movies, "Avatar")

    assert result["status"] == "found"
    assert result["movie_index"] == 0
    assert result["matches"] == [0, 3]


def test_find_movie_case_insensitive(movies):
    result = find_movie(movies, "AVATAR")

    assert result["status"] == "found"
    assert result["movie_index"] == 0


def test_find_movie_empty_input(movies):
    result = find_movie(movies, "")

    assert result == {
        "status": "empty",
        "movie_index": None,
        "matches": [],
    }


def test_find_movie_whitespace_input(movies):
    result = find_movie(movies, "   ")

    assert result["status"] == "empty"
    assert result["movie_index"] is None
    assert result["matches"] == []


def test_find_movie_similar_name(movies):
    result = find_movie(movies, "Avatr")

    assert result["status"] == "not_found"
    assert result["movie_index"] is None
    assert result["matches"]
    assert all(
        movies.loc[index, "name"] == "Avatar"
        for index in result["matches"]
    )


def test_find_movie_unknown_name(movies):
    result = find_movie(movies, "zzzzqqq")

    assert result["status"] == "not_found"
    assert result["movie_index"] is None
    assert result["matches"] == []
