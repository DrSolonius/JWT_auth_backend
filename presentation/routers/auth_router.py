from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    status,
)

from application.services.auth_service import AuthService
from domain.errores_auth import ErrorAutenticacion
from presentation.dependencies import UsuarioActualDep, get_auth_service
from presentation.schemas.dtos.auth_dto import (
    LoginDTO,
    RegistroDTO,
    TokenResponseDTO,
    UsuarioResponseDTO,
)
from presentation.security.cookies import (
    NOMBRE_COOKIE,
    borrar_cookie_refresh,
    poner_cookie_refresh,
)


router = APIRouter(prefix="/auth", tags=["Autenticación"])

AuthDep = Annotated[AuthService, Depends(get_auth_service)]
CookieRefresh = Annotated[str | None, Cookie(alias=NOMBRE_COOKIE)]


@router.post(
    "/registro",
    response_model=UsuarioResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def registrar(datos: RegistroDTO, service: AuthDep):
    try:
        usuario = service.registrar(
            email=datos.email,
            password=datos.password.get_secret_value(),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return UsuarioResponseDTO.model_validate(usuario)


@router.post("/login", response_model=TokenResponseDTO)
def login(datos: LoginDTO, response: Response, service: AuthDep):
    try:
        resultado = service.iniciar_sesion(
            email=datos.email,
            password=datos.password.get_secret_value(),
        )
    except ErrorAutenticacion as error:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    poner_cookie_refresh(response, resultado.refresh_token)
    return TokenResponseDTO(access_token=resultado.access_token)


@router.post("/refresh", response_model=TokenResponseDTO)
def refrescar(
    response: Response,
    service: AuthDep,
    refresh_token: CookieRefresh = None,
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Sesión expirada.")

    try:
        resultado = service.renovar(refresh_token)
    except ErrorAutenticacion as error:
        raise HTTPException(status_code=401, detail="Sesión expirada.") from error

    # El refresh token nuevo reemplaza al anterior en la cookie.
    poner_cookie_refresh(response, resultado.refresh_token)
    return TokenResponseDTO(access_token=resultado.access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(service: AuthDep, refresh_token: CookieRefresh = None):
    if refresh_token is not None:
        service.cerrar_sesion(refresh_token)

    # La cookie se borra en la respuesta que devolvemos.
    respuesta = Response(status_code=status.HTTP_204_NO_CONTENT)
    borrar_cookie_refresh(respuesta)
    return respuesta


@router.post("/logout-todos", status_code=status.HTTP_204_NO_CONTENT)
def logout_todos(usuario: UsuarioActualDep, service: AuthDep):
    service.cerrar_todas_las_sesiones(usuario)

    respuesta = Response(status_code=status.HTTP_204_NO_CONTENT)
    borrar_cookie_refresh(respuesta)
    return respuesta


@router.get("/me", response_model=UsuarioResponseDTO)
def yo(usuario: UsuarioActualDep):
    return UsuarioResponseDTO.model_validate(usuario)
