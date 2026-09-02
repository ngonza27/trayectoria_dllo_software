import bcrypt

"""
Slide 21 — Encriptación: passwords are never encrypted (reversible); they are
hashed with an algorithm designed for it. bcrypt embeds a random salt in the
returned hash, so hashing the same password twice yields two different hashes.
"""


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
