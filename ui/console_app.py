
from services.movie_service import find_movie
from services.criteria_service import get_criteria
from services.count_service import get_recommendation_count
from services.recommendation_service import recommend_movies
from ui.console_ui import display_recommendations


def run_console_app(movies):
    """اجرای نسخه کنسولی برنامه پیشنهاد فیلم."""

    print("=" * 60)
    print("MOVIE AND SERIES RECOMMENDATION SYSTEM")
    print("=" * 60)

    while True:
        movie_name = input(
            "\nEnter a movie name (or 'exit' to quit): "
        )

        if movie_name.strip().casefold() == "exit":
            print("\nThank you for using the recommendation system.")
            break

        search_result = find_movie(movies, movie_name)

        if search_result["status"] == "empty":
            print("Please enter a movie name.")
            continue

        if search_result["status"] == "not_found":
            print("Movie not found.")

            if search_result["matches"]:
                print("Similar movie names:")

                for index in search_result["matches"]:
                    print("-", movies.loc[index, "name"])

        else:
            movie_index = search_result["movie_index"]

            print("\nChoose recommendation criteria:")
            print("1. Genre")
            print("2. Director")
            print("3. Actors")
            print("4. Theme")
            print("5. Combined features")

            criteria_choice = input("Enter your choice (1-5): ")

            try:
                criteria = get_criteria(criteria_choice)
            except ValueError as error:
                print(error)
                continue

            print("\nChoose the number of recommendations:")
            print("1. 5 movies")
            print("2. 10 movies")
            print("3. 15 movies")

            count_choice = input("Enter your choice (1-3): ")

            try:
                recommendation_count = get_recommendation_count(
                    count_choice
                )
            except ValueError as error:
                print(error)
                continue

            try:
                result = recommend_movies(
                    movies,
                    movie_index,
                    criteria["columns"],
                    recommendation_count
                )

                display_recommendations(result)

            except (ValueError, IndexError) as error:
                print(f"\nUnable to generate recommendations: {error}")

        again = input(
            "\nDo you want to search for another movie? (y/n): "
        ).strip().casefold()

        if again != "y":
            print("\nThank you for using the recommendation system.")
            break
