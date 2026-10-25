# Movie and Series Recommendation System

<!-- معرفی کوتاه پروژه -->

## 1. Project Overview

This project is a Python-based application that recommends movies and TV series based on user preferences.

Users can search for a title and receive recommendations based on shared features such as genre, director, actors, and theme.

## 2. Features

<!-- قابلیت‌های اصلی برنامه -->

- Search for movies and TV series by name.
- Recommend titles based on selected criteria.
- Combine multiple recommendation criteria.
- Consider IMDb ratings in recommendation results.
- Select the number of recommendations.
- Handle invalid or missing movie names.
- Provide a graphical user interface using Streamlit.

## 3. Technologies

<!-- زبان برنامه‌نویسی و کتابخانه‌های استفاده‌شده -->

- Python
- Pandas
- Streamlit
- Scikit-learn
- OpenPyXL
- Pytest

## 4. Dataset

<!-- معرفی فایل اطلاعات فیلم‌ها و سریال‌ها -->

The application uses an Excel dataset containing movie and series information, including names, genres, directors, actors, themes, and IMDb ratings.

## 5. Recommendation Method

<!-- توضیح خلاصه روش پیشنهاد فیلم -->

The system compares movie and series features according to the selected criteria and identifies titles with relevant shared characteristics.

IMDb ratings are also considered according to the implemented recommendation logic.

## 6. Project Structure

<!-- معرفی پوشه‌ها و فایل‌های اصلی -->

- `app.py`: Main application and Streamlit interface.
- `data/`: Data-loading modules.
- `services/`: Search and recommendation logic.
- `utils/`: Helper functions.
- `ui/`: User-interface modules, if separated.
- `tests/`: Automated tests, if organized in this directory.
- `data_set/`: Dataset files, if stored in this directory.
- `README.md`: Project documentation.

## 7. Installation

<!-- نصب کتابخانه‌های موردنیاز -->

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 8. Run the Application

<!-- اجرای برنامه در ترمینال -->

Run the following command from the main project directory:

```bash
python -m streamlit run app.py
```

## 9. Run Tests

<!-- اجرای تست‌های خودکار -->

Run the tests using:

```bash
python -m pytest
```

## 10. Future Improvements

<!-- ایده‌های توسعه آینده -->

- Expand the dataset.
- Improve recommendation accuracy.
- Add more search filters.
- Improve the user interface.
- Introduce personalized recommendations.

## 11. License

<!-- مجوز استفاده از پروژه؛ قبل از انتخاب مجوز رسمی، شرایط آن را بررسی کن -->

No license has been specified for this project yet.
