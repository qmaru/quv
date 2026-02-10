import base64
import random
import secrets
import uuid

UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
NUMBER = "0123456789"
SYMBOLS = "!@#$%^&*()-_+="


def secure_str(n: int = 16) -> str:
    raw = secrets.token_bytes(n)
    b64 = base64.b64encode(raw).decode("ascii")
    return b64


def uuidv4_str() -> str:
    return str(uuid.uuid4())


def random_password(
    has_upper: bool,
    has_lower: bool,
    has_number: bool,
    has_symbol: bool,
    length: int,
) -> str:
    rng = random.SystemRandom()

    pools = []
    password_chars = []

    if has_upper:
        pools.append(UPPERCASE)
        password_chars.append(rng.choice(UPPERCASE))

    if has_lower:
        pools.append(LOWERCASE)
        password_chars.append(rng.choice(LOWERCASE))

    if has_number:
        pools.append(NUMBER)
        password_chars.append(rng.choice(NUMBER))

    if has_symbol:
        pools.append(SYMBOLS)
        password_chars.append(rng.choice(SYMBOLS))

    if not pools or length < len(password_chars):
        return ""

    all_chars = "".join(pools)

    for _ in range(len(password_chars), length):
        password_chars.append(rng.choice(all_chars))

    rng.shuffle(password_chars)

    return "".join(password_chars)


def generate_random():
    return {
        "password": random_password(True, True, True, True, 16),
        "secure": secure_str(),
        "uuidv4": uuidv4_str(),
    }


def cli():
    main()


def main():
    random_values = generate_random()
    print("Password:", random_values["password"])
    print("Secure  :", random_values["secure"])
    print("UUID v4 :", random_values["uuidv4"])


if __name__ == "__main__":
    main()
