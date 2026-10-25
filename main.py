
from data.data_loader import load_movies
from ui.console_app import run_console_app


try:
    movies = load_movies()
except (FileNotFoundError, ValueError, OSError) as error:
    print(f"Error loading Excel file: {error}")
    raise SystemExit(1)


print(
    f"Dataset loaded successfully: "
    f"{len(movies)} movies and series."
)


if __name__ == "__main__":
    run_console_app(movies)
