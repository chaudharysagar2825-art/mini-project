import secrets
import string


def generate_public_id(prefix: str = "USR") -> str:
    alphabet = string.ascii_uppercase + string.digits
    random_part = "".join(
        secrets.choice(alphabet)
        for _ in range(10)
    )

    return f"{prefix}-{random_part}"


def generate_case_code() -> str:
    return generate_public_id("CASE")