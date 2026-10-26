import hashlib
import secrets


def generar_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hashear_refresh_token(token: str) -> str:
    # SHA-256 alcanza: el token es aleatorio y largo, no se puede adivinar.
    return hashlib.sha256(token.encode()).hexdigest()
