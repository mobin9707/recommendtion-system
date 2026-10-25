
import pytest

from utils.text_utils import normalize_name


def test_normalize_name_lowercase():
    assert normalize_name("AVATAR") == "avatar"


def test_normalize_name_removes_extra_spaces():
    assert normalize_name("  Avatar  ") == "avatar"


def test_normalize_name_collapses_multiple_spaces():
    assert normalize_name("The    Dark   Knight") == "the dark knight"


def test_normalize_name_case_insensitive():
    assert normalize_name("The Dark Knight") == normalize_name(
        "THE DARK KNIGHT"
    )


@pytest.mark.parametrize(
    "movie_name, expected",
    [
        ("Avatar", "avatar"),
        ("  Titanic  ", "titanic"),
        ("The    Matrix", "the matrix"),
        ("INTERSTELLAR", "interstellar"),
    ],
)
def test_normalize_name_multiple_inputs(movie_name, expected):
    assert normalize_name(movie_name) == expected
