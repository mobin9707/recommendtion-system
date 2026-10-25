
from pathlib import Path
import logging
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_FILE = BASE_DIR / "data_set" / "movies_real_500_quoted_imdb.xlsx"

logger = logging.getLogger("movie_app")

REQUIRED_COLUMNS = ["name", "genre", "director", "actors", "theme", "imdb"]
TEXT_COLUMNS = ["genre", "director", "actors", "theme"]


def load_movies():
    """Load, validate, and clean the movie dataset."""

    # Check whether the Excel file exists.
    if not EXCEL_FILE.exists():
        logger.error("Movie dataset not found: %s", EXCEL_FILE)
        raise FileNotFoundError(f"Movie dataset not found: {EXCEL_FILE}")

    # Read the Excel file.
    movies = pd.read_excel(EXCEL_FILE)

    logger.info("Movie dataset loaded successfully.")
    logger.info("Number of movies and series: %s", len(movies))

    # Normalize column names.
    movies.columns = [
        str(column).strip().lower()
        for column in movies.columns
    ]

    # Support the legacy 'imbd' column name.
    if "imdb" not in movies.columns and "imbd" in movies.columns:
        movies = movies.rename(columns={"imbd": "imdb"})

    # Validate required columns.
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in movies.columns
    ]

    if missing_columns:
        logger.error(
            "Missing required columns: %s",
            ", ".join(missing_columns),
        )
        raise ValueError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    # Remove rows without valid movie or series names.
    movies = movies.dropna(subset=["name"]).copy()
    movies["name"] = movies["name"].astype(str).str.strip()
    movies = movies[movies["name"] != ""].copy()

    # Clean text columns.
    for column in TEXT_COLUMNS:
        movies[column] = (
            movies[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Convert IMDb ratings to numeric values.
    movies["imdb"] = pd.to_numeric(
        movies["imdb"]
        .astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )

    # Log missing or invalid IMDb ratings.
    invalid_imdb_count = movies["imdb"].isna().sum()

    if invalid_imdb_count > 0:
        logger.warning(
            "Found %s movies and series with missing or invalid IMDb ratings.",
            invalid_imdb_count,
        )

    # Reset row indexes.
    movies.reset_index(drop=True, inplace=True)

    # Ensure that the dataset contains valid rows.
    if movies.empty:
        logger.error("The dataset contains no valid movies.")
        raise ValueError("The dataset contains no valid movies.")

    logger.info(
        "Dataset validation completed successfully. Valid rows: %s",
        len(movies),
    )

    return movies
