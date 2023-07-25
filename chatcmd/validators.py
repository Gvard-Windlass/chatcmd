import re


def validate_password(password: str):
    digits = re.findall(r"\d", password)
    chars = re.findall(r"[a-zA-Z]", password)
    symbols = re.findall(r"[!@#\"'$;%^:&?*\(\)\[\]\.,{}]", password)
    if all([digits, chars, symbols]):
        return all(len(x) >= 3 for x in [digits, chars, symbols])
    return False


def validate_username(name: str):
    check = re.fullmatch(r"[a-zA-Z\d_]+", name)
    if check and len(name) > 3 and len(name) <= 10:
        return True
    return False
