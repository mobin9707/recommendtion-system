
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


def build_model(movies, selected_columns):
    """ساخت مدل پیشنهاد بر اساس ویژگی‌های انتخاب‌شده."""

    feature_text = movies[selected_columns].agg(
        " ".join,
        axis=1
    ).str.strip()

    if feature_text.eq("").all():
        raise ValueError(
            "The selected criteria contain no usable information."
        )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        strip_accents="unicode",
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(feature_text)

    model = NearestNeighbors(
        metric="cosine",
        algorithm="brute"
    )

    model.fit(tfidf_matrix)

    return tfidf_matrix, model


def split_values(value):
    """تقسیم مقادیر جداشده با ویرگول یا جداکننده‌های مشابه."""

    return {
        item.strip().casefold()
        for item in re.split(r"[,;|/]", str(value))
        if item.strip()
    }


def find_common_features(source, candidate):
    """پیدا کردن ویژگی‌های مشترک دو فیلم."""

    common = []

    for column, label in [
        ("genre", "Genre"),
        ("director", "Director"),
        ("actors", "Actors")
    ]:
        source_value = str(source[column]).strip()
        candidate_value = str(candidate[column]).strip()

        if not source_value or not candidate_value:
            continue

        if column == "director":
            if source_value.casefold() == candidate_value.casefold():
                common.append(f"{label}: {candidate_value}")
        else:
            shared = split_values(source_value) & split_values(
                candidate_value
            )

            if shared:
                display_values = []

                for item in re.split(r"[,;|/]", candidate_value):
                    item = item.strip()

                    if item.casefold() in shared:
                        display_values.append(item)

                common.append(
                    f"{label}: {', '.join(display_values)}"
                )

    source_theme = set(
        re.findall(r"\b\w+\b", str(source["theme"]).casefold())
    )

    candidate_theme = set(
        re.findall(r"\b\w+\b", str(candidate["theme"]).casefold())
    )

    shared_theme_words = source_theme & candidate_theme

    if shared_theme_words:
        common.append(
            "Shared theme keywords: "
            + ", ".join(sorted(shared_theme_words)[:8])
        )

    return common


def recommend_movies(
    movies,
    movie_index,
    selected_columns,
    recommendation_count
):
    """تولید پیشنهادها و برگرداندن نتایج بدون نمایش مستقیم."""

    if not 0 <= movie_index < len(movies):
        raise IndexError("Invalid movie index.")

    if recommendation_count < 1:
        raise ValueError("Recommendation count must be positive.")

    if not selected_columns:
        raise ValueError("Select at least one recommendation criterion.")

    missing_columns = [
        column for column in selected_columns
        if column not in movies.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {', '.join(missing_columns)}"
        )

    source_movie = movies.iloc[movie_index].copy()

    tfidf_matrix, model = build_model(
        movies,
        selected_columns
    )

    neighbors_count = min(
        len(movies),
        recommendation_count + 1
    )

    distances, indices = model.kneighbors(
        tfidf_matrix[movie_index],
        n_neighbors=neighbors_count
    )

    candidates = []

    for distance, index in zip(distances[0], indices[0]):
        if index == movie_index:
            continue

        candidate = movies.iloc[index].copy()

        candidate["similarity"] = 1 - float(distance)

        candidate["common_features"] = find_common_features(
            source_movie,
            candidate
        )

        candidates.append(candidate)

    recommendations = pd.DataFrame(candidates)

    if not recommendations.empty:
        recommendations = recommendations.sort_values(
            by=["imdb", "similarity"],
            ascending=[False, False],
            na_position="last"
        )

        recommendations = recommendations.head(
            recommendation_count
        )

    return {
        "source_movie": source_movie,
        "recommendations": recommendations,
        "selected_columns": selected_columns
    }
