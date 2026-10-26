from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from domain.errores_auth import TokenInvalido
from infrastructure.security import config


class JwtService:
    def crear_access_token(self, usuario_id: int, version: int) -> str:
        ahora = datetime.now(timezone.utc)
        payload = {
            "sub": str(usuario_id),
            "type": "access",
            "ver": version,
            "iat": ahora,
            "exp": ahora + timedelta(minutes=config.ACCESS_TOKEN_MINUTOS),
            "jti": uuid4().hex,
        }

        return jwt.encode(
            payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITMO
        )

    def decodificar_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET,
                algorithms=[config.JWT_ALGORITMO],  # lista fija
                options={"require": ["exp", "sub", "iat"]},
            )
        except jwt.InvalidTokenError as error:  # incluye ExpiredSignatureError
            raise TokenInvalido() from error

        if payload.get("type") != "access":
            raise TokenInvalido()

        return payload
