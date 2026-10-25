
import pandas as pd
import pytest

from data import data_loader


@pytest.fixture
def valid_movies():
    return pd.DataFrame(
        {
            "name": ["Avatar", "Titanic", "  Interstellar  "],
            "genre": ["Sci-Fi", "Drama", None],
            "director": ["James Cameron", "James Cameron", "Nolan"],
            "actors": ["Actor A", "Actor B", "Actor C"],
            "theme": ["Space", "Love", "Science"],
            "imdb": ["7.9", "8,0", "invalid"],
        }
    )


def write_excel(monkeypatch, tmp_path, movies):
    file_path = tmp_path / "test_movies.xlsx"
    movies.to_excel(file_path, index=False)

    monkeypatch.setattr(data_loader, "EXCEL_FILE", file_path)


def test_load_movies_success(monkeypatch, tmp_path, valid_movies):
    write_excel(monkeypatch, tmp_path, valid_movies)

    result = data_loader.load_movies()

    assert len(result) == 3
    assert list(result.index) == [0, 1, 2]
    assert result.loc[0, "name"] == "Avatar"
    assert result.loc[2, "name"] == "Interstellar"
    assert result.loc[2, "genre"] == ""


def test_load_movies_normalizes_column_names(
    monkeypatch, tmp_path
):
    movies = pd.DataFrame(
        {
            " NAME ": ["Avatar"],
            " GENRE ": ["Sci-Fi"],
            " DIRECTOR ": ["Director A"],
            " ACTORS ": ["Actor A"],
            " THEME ": ["Space"],
            " IMDB ": [7.9],
        }
    )

    write_excel(monkeypatch, tmp_path, movies)

    result = data_loader.load_movies()

    assert all(
        column in result.columns
        for column in data_loader.REQUIRED_COLUMNS
    )


def test_load_movies_supports_legacy_imbd(
    monkeypatch, tmp_path
):
    movies = pd.DataFrame(
        {
            "name": ["Avatar"],
            "genre": ["Sci-Fi"],
            "director": ["Director A"],
            "actors": ["Actor A"],
            "theme": ["Space"],
            "imbd": [7.9],
        }
    )

    write_excel(monkeypatch, tmp_path, movies)

    result = data_loader.load_movies()

    assert "imdb" in result.columns
    assert "imbd" not in result.columns
    assert result.loc[0, "imdb"] == 7.9


def test_load_movies_removes_empty_names(
    monkeypatch, tmp_path
):
    movies = pd.DataFrame(
        {
            "name": ["Avatar", None, "   ", "Titanic"],
            "genre": ["Sci-Fi", "Drama", "Action", "Drama"],
            "director": ["A", "B", "C", "D"],
            "actors": ["A", "B", "C", "D"],
            "theme": ["Space", "Love", "War", "Love"],
            "imdb": [7.9, 8.0, 6.0, 8.0],
        }
    )

    write_excel(monkeypatch, tmp_path, movies)

    result = data_loader.load_movies()

    assert result["name"].tolist() == ["Avatar", "Titanic"]
    assert len(result) == 2


def test_load_movies_converts_imdb_values(
    monkeypatch, tmp_path
):
    movies = pd.DataFrame(
        {
            "name": ["Avatar", "Titanic", "Unknown"],
            "genre": ["Sci-Fi", "Drama", "Drama"],
            "director": ["A", "B", "C"],
            "actors": ["A", "B", "C"],
            "theme": ["Space", "Love", "Life"],
            "imdb": ["7.9", "8,0", "invalid"],
        }
    )

    write_excel(monkeypatch, tmp_path, movies)

    result = data_loader.load_movies()

    assert result.loc[0, "imdb"] == 7.9
    assert result.loc[1, "imdb"] == 8.0
    assert pd.isna(result.loc[2, "imdb"])


def test_load_movies_raises_when_file_missing(
    monkeypatch, tmp_path
):
    missing_file = tmp_path / "missing.xlsx"

    monkeypatch.setattr(
        data_loader, "EXCEL_FILE", missing_file
    )

    with pytest.raises(FileNotFoundError):
        data_loader.load_movies()


def test_load_movies_raises_for_missing_columns(
    monkeypatch, tmp_path
):
    movies = pd.DataFrame(
        {
            "name": ["Avatar"],
            "genre": ["Sci-Fi"],
        }
    )

    write_excel(monkeypatch, tmp_path, movies)

    with pytest.raises(ValueError, match="Missing required columns"):
        data_loader.load_movies()


def test_load_movies_raises_when_no_valid_movies(
    monkeypatch, tmp_path
):
    movies = pd.DataFrame(
        {
            "name": [None, "   "],
            "genre": ["Sci-Fi", "Drama"],
            "director": ["A", "B"],
            "actors": ["A", "B"],
            "theme": ["Space", "Love"],
            "imdb": [7.9, 8.0],
        }
    )

    write_excel(monkeypatch, tmp_path, movies)

    with pytest.raises(
        ValueError, match="no valid movies"
    ):
        data_loader.load_movies()
