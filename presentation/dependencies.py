from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from application.services.auth_service import AuthService
from application.services.curso_service import CursoService
from application.services.estudiante_service import EstudianteService
from application.services.inscripcion_service import InscripcionService
from domain.errores_auth import TokenInvalido
from domain.usuario import Usuario
from infrastructure.database import SessionLocal
from infrastructure.repositories.curso_repository import CursoRepository
from infrastructure.repositories.estudiante_repository import (
    EstudianteRepository,
)
from infrastructure.repositories.inscripcion_repository import (
    InscripcionRepository,
)
from infrastructure.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from infrastructure.repositories.usuario_repository import UsuarioRepository
from infrastructure.security.jwt_service import JwtService
from infrastructure.security.password_hasher import PasswordHasher


# Una sola instancia por proceso: crearlas cuesta (el hasher calcula el hash ficticio).
_hasher = PasswordHasher()
_jwt_service = JwtService()


def get_session() -> Iterator[Session]:
    """Abre una sesión por solicitud y la cierra al terminar."""
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]


def get_estudiante_service(session: SessionDep) -> EstudianteService:
    return EstudianteService(
        EstudianteRepository(session),
        InscripcionRepository(session),
    )


def get_curso_service(session: SessionDep) -> CursoService:
    return CursoService(
        CursoRepository(session),
        InscripcionRepository(session),
    )


def get_inscripcion_service(session: SessionDep) -> InscripcionService:
    return InscripcionService(
        InscripcionRepository(session),
        EstudianteRepository(session),
        CursoRepository(session),
    )


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        UsuarioRepository(session),
        RefreshTokenRepository(session),
        _hasher,
        _jwt_service,
    )


# auto_error=False: respondemos nosotros siempre 401 con WWW-Authenticate.
bearer = HTTPBearer(auto_error=False)
CredencialesDep = Annotated[
    HTTPAuthorizationCredentials | None, Depends(bearer)
]


def get_usuario_actual(
    credenciales: CredencialesDep,
    session: SessionDep,
) -> Usuario:
    no_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credenciales is None:
        raise no_autenticado

    try:
        payload = _jwt_service.decodificar_access_token(credenciales.credentials)
    except TokenInvalido:
        raise no_autenticado from None

    usuario = UsuarioRepository(session).obtener_por_id(int(payload["sub"]))

    if (
        usuario is None
        or not usuario.activo
        or usuario.token_version != payload.get("ver")
    ):
        raise no_autenticado

    return usuario


UsuarioActualDep = Annotated[Usuario, Depends(get_usuario_actual)]
