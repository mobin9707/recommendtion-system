
import pandas as pd


def display_recommendations(result):
    """نمایش پیشنهادهای فیلم در ترمینال."""

    source_movie = result["source_movie"]
    recommendations = result["recommendations"]
    selected_columns = result["selected_columns"]

    print("\n" + "=" * 60)
    print("MOVIE AND SERIES RECOMMENDATIONS")
    print("=" * 60)

    print(f"\nSelected title: {source_movie['name']}")
    print(f"Recommendation criteria: {', '.join(selected_columns)}")
    print(f"Recommendations found: {len(recommendations)}")

    print("\nSelected title information:")

    for column in ["genre", "director", "actors", "theme"]:
        print(f"{column.title()}: {source_movie[column] or 'N/A'}")

    print(
        f"IMDb: {source_movie['imdb']}"
        if pd.notna(source_movie["imdb"])
        else "IMDb: N/A"
    )

    if recommendations.empty:
        print("\nNo recommendations are available.")
        print("=" * 60)
        return

    for number, (_, movie) in enumerate(
        recommendations.iterrows(),
        start=1
    ):
        print("\n" + "-" * 60)
        print(f"Recommendation #{number}")

        for column in ["name", "genre", "director", "actors", "theme"]:
            print(f"{column.title()}: {movie[column] or 'N/A'}")

        print(
            f"IMDb: {movie['imdb']}"
            if pd.notna(movie["imdb"])
            else "IMDb: N/A"
        )

        if movie["common_features"]:
            print("Common features:")

            for feature in movie["common_features"]:
                print(f"  - {feature}")
        else:
            print("Common features: No exact shared features identified.")

    print("\n" + "=" * 60)
