import html
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from config.logging_config import setup_logging
# --------------------------------------------------
# Page configuration
# --------------------------------------------------
logger = setup_logging()
logger.info("Movie recommendation app started.")

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="centered",
)


# --------------------------------------------------
# CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #ffffff;
    }

    .block-container {
        max-width: 900px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    .welcome-title {
        text-align: center;
        color: #111111;
        font-family: 'Georgia', serif;
        font-size: clamp(32px, 5vw, 48px);
        font-weight: 700;
        margin-bottom: 8px;
    }

    .welcome-subtitle {
        text-align: center;
        color: #a0a0a0;
        font-family: 'Georgia', serif;
        font-size: 25px;
        margin-bottom: 65px;
    }

    .section-title {
        color: #171717;
        font-size: 19px;
        font-weight: 600;
        margin-top: 22px;
        margin-bottom: 12px;
    }

    div[data-testid="stTextInput"] input {
        font-family: Arial, sans-serif !important;
        font-size: 16px !important;
        color: #171717 !important;
        background: #ffffff !important;
        border: 1px solid #dedede !important;
        border-radius: 24px !important;
        min-height: 52px;
        padding-left: 20px !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border: 1px solid #bdbdbd !important;
        box-shadow: none !important;
        outline: none !important;
    }

    div[data-testid="stRadio"] label {
        color: #292929 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 14px;
    }

    div[data-testid="stRadio"] div[role="radio"] {
        gap: 7px;
    }

    div[data-testid="stRadio"] div[role="radio"] > div:first-child {
        border-color: #a7a7a7 !important;
    }

    div[data-testid="stRadio"] div[role="radio"][aria-checked="true"]
    > div:first-child {
        border-color: #111111 !important;
        background-color: #111111 !important;
    }

    div[data-testid="stFormSubmitButton"] {
        display: none;
    }

    .movie-card {
        border: 1px solid #e8e8e8;
        border-radius: 14px;
        padding: 20px;
        margin: 12px 0;
        background: #ffffff;
    }

    .movie-card h3 {
        color: #111111;
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 21px;
    }

    .movie-info {
        color: #555555;
        line-height: 1.8;
        overflow-wrap: anywhere;
    }

    .movie-score {
        color: #111111;
        font-weight: 700;
    }

    .shared-features {
        color: #666666;
        font-size: 14px;
        margin-top: 10px;
    }

    .error-message {
        color: #d93025;
        font-size: 14px;
        margin-top: 8px;
    }

    div.stButton > button {
        border-radius: 24px;
        border: 1px solid #dddddd;
        background: #ffffff;
        color: #171717;
        min-height: 42px;
    }

    div.stButton > button:hover {
        border-color: #111111;
        color: #111111;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

def load_movies():
    possible_paths = [
        Path("data_set/movies_real_500_quoted_imdb.xlsx"),
        Path("data/movies_real_500_quoted_imdb.xlsx"),
        Path("movies_real_500_quoted_imdb.xlsx"),
    ]

    file_path = next(
        (path for path in possible_paths if path.exists()),
        None,
    )

    if file_path is None:
        raise FileNotFoundError(
            "Dataset not found. Check the Excel file path."
        )

    data = pd.read_excel(file_path)

    data.columns = [
        str(column).strip().lower()
        for column in data.columns
    ]

    aliases = {
        "name": ["name", "title", "movie", "series"],
        "genre": ["genre", "genres"],
        "director": ["director", "directors"],
        "actors": ["actors", "actor", "cast", "stars"],
        "theme": ["theme", "topic", "plot", "description"],
        "imdb": ["imdb", "imbd", "rating", "score"],
    }

    for standard_name, possible_names in aliases.items():
        if standard_name not in data.columns:
            for possible_name in possible_names:
                if possible_name in data.columns:
                    data[standard_name] = data[possible_name]
                    break

        if standard_name not in data.columns:
            data[standard_name] = ""

    data["name"] = data["name"].fillna("").astype(str).str.strip()

    data = data[data["name"] != ""].copy()
    data = data.reset_index(drop=True)

    for column in ["genre", "director", "actors", "theme"]:
        data[column] = data[column].fillna("").astype(str).str.strip()

    data["imdb"] = pd.to_numeric(data["imdb"], errors="coerce")

    return data


# --------------------------------------------------
# Text utilities
# --------------------------------------------------

def normalize_text(value):
    value = str(value).casefold().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def split_values(value):
    if pd.isna(value):
        return set()

    parts = re.split(r"[,;|/\n]+", str(value))

    return {
        normalize_text(part)
        for part in parts
        if normalize_text(part)
    }


# --------------------------------------------------
# Find a movie
# --------------------------------------------------

def find_movie(data, query):
    query_normalized = normalize_text(query)

    if not query_normalized:
        return None

    exact_matches = data.index[
        data["name"].apply(normalize_text) == query_normalized
    ].tolist()

    if exact_matches:
        return exact_matches[0]

    partial_matches = data.index[
        data["name"].apply(
            lambda name: query_normalized in normalize_text(name)
        )
    ].tolist()

    if len(partial_matches) == 1:
        return partial_matches[0]

    return None


# --------------------------------------------------
# Recommendation logic
# --------------------------------------------------

FEATURE_COLUMNS = {
    "Genre": ["genre"],
    "Director": ["director"],
    "Actors": ["actors"],
    "Theme": ["theme"],
    "Combined": ["genre", "director", "actors", "theme"],
}


def get_movie_features(movie, columns):
    features = {}

    for column in columns:
        features[column] = split_values(movie[column])

    return features


def recommend_movies(data, movie_index, criterion, amount):
    selected_movie = data.loc[movie_index]
    columns = FEATURE_COLUMNS[criterion]

    selected_features = get_movie_features(
        selected_movie,
        columns,
    )

    results = []

    for candidate_index, candidate in data.iterrows():
        if candidate_index == movie_index:
            continue

        candidate_features = get_movie_features(
            candidate,
            columns,
        )

        common_features = []
        matched_categories = 0

        for column in columns:
            common = (
                selected_features[column]
                & candidate_features[column]
            )

            if common:
                matched_categories += 1

                for feature in sorted(common):
                    common_features.append(
                        f"{column.title()}: {feature}"
                    )

        if not common_features:
            continue

        imdb_score = candidate["imdb"]

        if pd.isna(imdb_score):
            imdb_score = 0.0

        results.append({
            "index": candidate_index,
            "name": candidate["name"],
            "genre": candidate["genre"],
            "director": candidate["director"],
            "actors": candidate["actors"],
            "theme": candidate["theme"],
            "imdb": imdb_score,
            "common_features": common_features,
            "matched_categories": matched_categories,
            "common_count": len(common_features),
        })

    results.sort(
        key=lambda item: (
            item["matched_categories"],
            item["common_count"],
            item["imdb"],
        ),
        reverse=True,
    )

    return results[:int(amount)]


# --------------------------------------------------
# Display movie information
# --------------------------------------------------

def safe_text(value):
    if pd.isna(value) or str(value).strip() == "":
        return "Not available"

    return html.escape(str(value))


def display_movie(movie, heading=""):
    title = safe_text(movie["name"])
    genre = safe_text(movie["genre"])
    director = safe_text(movie["director"])
    actors = safe_text(movie["actors"])
    theme = safe_text(movie["theme"])

    imdb_value = movie["imdb"]

    if pd.isna(imdb_value):
        imdb_text = "Not available"
    else:
        imdb_text = f"{imdb_value:.1f}/10"

    st.markdown(
        f"""
        <div class="movie-card">
            <h3>{heading}{title}</h3>
            <div class="movie-info">
                <b>Genre:</b> {genre}<br>
                <b>Director:</b> {director}<br>
                <b>Actors:</b> {actors}<br>
                <b>Theme:</b> {theme}<br>
                <b>IMDb:</b>
                <span class="movie-score">{imdb_text}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_recommendation(item, number):
    title = safe_text(item["name"])
    genre = safe_text(item["genre"])
    director = safe_text(item["director"])
    actors = safe_text(item["actors"])
    theme = safe_text(item["theme"])

    imdb_value = item["imdb"]

    if pd.isna(imdb_value):
        imdb_text = "Not available"
    else:
        imdb_text = f"{imdb_value:.1f}/10"

    common_features = ", ".join(item["common_features"])
    common_features = safe_text(common_features)

    st.markdown(
        f"""
        <div class="movie-card">
            <h3>{number}. {title}</h3>
            <div class="movie-info">
                <b>Genre:</b> {genre}<br>
                <b>Director:</b> {director}<br>
                <b>Actors:</b> {actors}<br>
                <b>Theme:</b> {theme}<br>
                <b>IMDb:</b>
                <span class="movie-score">{imdb_text}</span>
            </div>
            <div class="shared-features">
                <b>Shared features:</b> {common_features}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Load data and handle errors
# --------------------------------------------------

try:
    movies = load_movies()
except (FileNotFoundError, OSError, ValueError) as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()


# --------------------------------------------------
# Page heading
# --------------------------------------------------

st.markdown(
    '<div class="welcome-title">Welcome to the Recommendation System</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="welcome-subtitle">Find Your Movies</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Search form
# Press Enter in the movie input to submit
# --------------------------------------------------

if "search_result" not in st.session_state:
    st.session_state.search_result = None

if "search_error" not in st.session_state:
    st.session_state.search_error = None

with st.form("movie_search_form", clear_on_submit=False):
    st.markdown(
        '<div class="section-title">Search for a movie or series</div>',
        unsafe_allow_html=True,
    )

    movie_query = st.text_input(
        "Movie name",
        placeholder="Enter a movie or series name...",
        label_visibility="collapsed",
        key="movie_query",
    )

    st.markdown(
        '<div class="section-title">Recommendation Criteria</div>',
        unsafe_allow_html=True,
    )

    criterion = st.radio(
        "Choose a criterion",
        ["Genre", "Director", "Actors", "Theme", "Combined"],
        horizontal=True,
        index=None,
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="section-title">Number of Recommendations</div>',
        unsafe_allow_html=True,
    )

    amount = st.radio(
        "Choose the number of recommendations",
        [5, 10, 15],
        horizontal=True,
        index=None,
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button("Search")


# --------------------------------------------------
# Validate and perform search
# --------------------------------------------------

if submitted:
    st.session_state.search_result = None
    st.session_state.search_error = None

    if not movie_query.strip():
        st.session_state.search_error = (
            "movie",
            "Please enter a movie or series name.",
        )

    elif criterion is None:
        st.session_state.search_error = (
            "criterion",
            "Please select a recommendation criterion.",
        )

    elif amount is None:
        st.session_state.search_error = (
            "amount",
            "Please select the number of recommendations.",
        )

    else:
        movie_index = find_movie(movies, movie_query)

        if movie_index is None:
            st.session_state.search_error = (
                "movie",
                "Movie or series not found. Check the spelling and try again.",
            )
        else:
            recommendations = recommend_movies(
                movies,
                movie_index,
                criterion,
                amount,
            )

            st.session_state.search_result = {
                "movie_index": movie_index,
                "recommendations": recommendations,
                "criterion": criterion,
                "amount": amount,
            }


# --------------------------------------------------
# Display validation errors
# --------------------------------------------------

if st.session_state.search_error is not None:
    error_type, error_message = st.session_state.search_error

    st.markdown(
        f'<div class="error-message">{html.escape(error_message)}</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Display search results
# --------------------------------------------------

result = st.session_state.search_result

if result is not None:
    st.divider()

    selected_movie = movies.loc[result["movie_index"]]

    st.markdown("## Selected Movie")
    display_movie(selected_movie)

    st.markdown("## Recommended Movies")

    st.caption(
        f"Criteria: {result['criterion']} · "
        f"Showing up to {result['amount']} recommendations"
    )

    recommendations = result["recommendations"]

    if recommendations:
        for number, item in enumerate(recommendations, start=1):
            display_recommendation(item, number)
    else:
        st.info(
            "No matching recommendations were found for this criterion."
        )

    if st.button("Search Another Movie"):
        st.session_state.search_result = None
        st.session_state.search_error = None
        st.session_state.movie_query = ""
        st.rerun()
