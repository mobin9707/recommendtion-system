
import pandas as pd
import pytest

from services.recommendation_service import (
    build_model,
    split_values,
    find_common_features,
    recommend_movies,
)


@pytest.fixture
def movies():
    return pd.DataFrame(
        {
            "name": [
                "Space Adventure",
                "Space Journey",
                "Ocean Mystery",
                "Space Mission",
            ],
            "genre": [
                "Sci-Fi, Adventure",
                "Sci-Fi, Action",
                "Mystery, Drama",
                "Sci-Fi, Adventure",
            ],
            "director": [
                "Alex Smith",
                "Alex Smith",
                "Jane Brown",
                "Chris Green",
            ],
            "actors": [
                "Tom Lee, Sara Kim",
                "Tom Lee, John Park",
                "Emma White, Sara Kim",
                "Tom Lee, Sara Kim",
            ],
            "theme": [
                "space exploration friendship",
                "space exploration courage",
                "ocean mystery friendship",
                "space exploration friendship",
            ],
            "imdb": [7.0, 8.5, 9.0, 7.5],
        }
    )


def test_split_values():
    result = split_values("Sci-Fi, Adventure; Action | Drama")

    assert result == {
        "sci-fi",
        "adventure",
        "action",
        "drama",
    }


def test_split_values_ignores_extra_spaces():
    result = split_values("  Drama , Action  ")

    assert result == {"drama", "action"}


def test_find_common_features(movies):
    source = movies.iloc[0]
    candidate = movies.iloc[1]

    result = find_common_features(source, candidate)

    assert "Genre: Sci-Fi" in result
    assert "Director: Alex Smith" in result
    assert "Actors: Tom Lee" in result
    assert any(
        item.startswith("Shared theme keywords:")
        for item in result
    )


def test_build_model(movies):
    matrix, model = build_model(
        movies,
        ["genre", "theme"],
    )

    assert matrix.shape[0] == len(movies)
    assert matrix.shape[1] > 0
    assert model is not None


def test_build_model_rejects_empty_features():
    empty_movies = pd.DataFrame(
        {
            "genre": ["", "  ", ""],
        }
    )

    with pytest.raises(ValueError):
        build_model(empty_movies, ["genre"])


def test_recommend_movies_returns_expected_structure(movies):
    result = recommend_movies(
        movies,
        movie_index=0,
        selected_columns=["genre", "theme"],
        recommendation_count=2,
    )

    assert result["source_movie"]["name"] == "Space Adventure"
    assert list(result.keys()) == [
        "source_movie",
        "recommendations",
        "selected_columns",
    ]
    assert len(result["recommendations"]) == 2
    assert "similarity" in result["recommendations"].columns
    assert "common_features" in result["recommendations"].columns


def test_recommendations_exclude_source_movie(movies):
    result = recommend_movies(
        movies,
        movie_index=0,
        selected_columns=["genre", "theme"],
        recommendation_count=3,
    )

    recommended_names = result["recommendations"]["name"].tolist()

    assert "Space Adventure" not in recommended_names


def test_recommendations_sorted_by_imdb(movies):
    result = recommend_movies(
        movies,
        movie_index=0,
        selected_columns=["genre", "theme"],
        recommendation_count=3,
    )

    scores = result["recommendations"]["imdb"].tolist()

    assert scores == sorted(scores, reverse=True)


def test_recommendations_reject_invalid_index(movies):
    with pytest.raises(IndexError):
        recommend_movies(
            movies,
            movie_index=100,
            selected_columns=["genre"],
            recommendation_count=2,
        )


def test_recommendations_reject_zero_count(movies):
    with pytest.raises(ValueError):
        recommend_movies(
            movies,
            movie_index=0,
            selected_columns=["genre"],
            recommendation_count=0,
        )


def test_recommendations_reject_empty_criteria(movies):
    with pytest.raises(ValueError):
        recommend_movies(
            movies,
            movie_index=0,
            selected_columns=[],
            recommendation_count=2,
        )


def test_recommendations_reject_missing_column(movies):
    with pytest.raises(ValueError):
        recommend_movies(
            movies,
            movie_index=0,
            selected_columns=["unknown_column"],
            recommendation_count=2,
        )
