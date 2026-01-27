import re

ACCOUNT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

def is_valid_account_name(account_name):
    if not account_name:
        return False
    return bool(ACCOUNT_NAME_PATTERN.fullmatch(account_name))
