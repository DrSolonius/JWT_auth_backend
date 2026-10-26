from fastapi import Response

from infrastructure.security import config


NOMBRE_COOKIE = "refresh_token"
RUTA_COOKIE = "/auth"


def poner_cookie_refresh(response: Response, token: str) -> None:
    response.set_cookie(
        key=NOMBRE_COOKIE,
        value=token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="strict",
        path=RUTA_COOKIE,
        max_age=config.REFRESH_TOKEN_DIAS * 24 * 60 * 60,
    )


def borrar_cookie_refresh(response: Response) -> None:
    response.delete_cookie(
        NOMBRE_COOKIE,
        path=RUTA_COOKIE,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="strict",
    )
