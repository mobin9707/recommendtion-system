import re

def normalize_name(name):
    return re.sub(r"\s+", " ", str(name)).strip().casefold()
#یکسان کردن نام فیلم ها