
COUNT_OPTIONS = {
    "1": 5,
    "2": 10,
    "3": 15
}


def get_recommendation_count(choice):
    """
    تبدیل انتخاب کاربر به تعداد فیلم‌های پیشنهادی.
    این تابع ورودی کنسول نمی‌گیرد و چیزی چاپ نمی‌کند.
    """
    choice = str(choice).strip()

    if choice not in COUNT_OPTIONS:
        raise ValueError(
            "Invalid choice. Please enter 1, 2, or 3."
        )

    return COUNT_OPTIONS[choice]
