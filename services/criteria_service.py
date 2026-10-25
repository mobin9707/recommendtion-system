
FEATURE_OPTIONS = {
    "1": {
        "name": "Genre",
        "columns": ["genre"]
    },
    "2": {
        "name": "Director",
        "columns": ["director"]
    },
    "3": {
        "name": "Actors",
        "columns": ["actors"]
    },
    "4": {
        "name": "Theme",
        "columns": ["theme"]
    },
    "5": {
        "name": "Combined",
        "columns": ["genre", "director", "actors", "theme"]
    }
}


def get_criteria(choice):
    """برگرداندن معیار انتخاب‌شده بدون دریافت ورودی کنسول."""

    choice = str(choice).strip()

    if choice not in FEATURE_OPTIONS:
        raise ValueError("Invalid choice. Please enter a number from 1 to 5.")

    return FEATURE_OPTIONS[choice]
