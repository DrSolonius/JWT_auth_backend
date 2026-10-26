from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from domain.errores_auth import CredencialesInvalidas, CuentaBloqueada, TokenInvalido
from domain.refresh_token import RefreshToken
from domain.usuario import Usuario
from infrastructure.security import config
from infrastructure.security.refresh_token_util import (
    generar_refresh_token,
    hashear_refresh_token,
)


@dataclass(frozen=True)
class ResultadoAuth:
    usuario: Usuario
    access_token: str
    refresh_token: str


class AuthService:
    def __init__(self, usuario_repository, refresh_repository,
                 hasher, jwt_service) -> None:
        self.usuario_repository = usuario_repository
        self.refresh_repository = refresh_repository
        self.hasher = hasher
        self.jwt_service = jwt_service

    def registrar(self, email: str, password: str) -> Usuario:
        if self.usuario_repository.obtener_por_email(email):
            raise ValueError("No se pudo completar el registro.")
        usuario = Usuario(
            email=email,
            password_hash=self.hasher.hashear(password),
        )
        return self.usuario_repository.crear(usuario)

    def iniciar_sesion(self, email: str, password: str) -> ResultadoAuth:
        usuario = self.usuario_repository.obtener_por_email(email)
        if usuario is None:
            self.hasher.verificar(password, self.hasher.hash_ficticio)
            raise CredencialesInvalidas()
        ahora = datetime.now(timezone.utc)
        if usuario.esta_bloqueado(ahora):
            raise CuentaBloqueada()
        if not self.hasher.verificar(password, usuario.password_hash):
            usuario.registrar_fallo(ahora)
            self.usuario_repository.actualizar(usuario)
            raise CredencialesInvalidas()
        if not usuario.activo:
            raise CredencialesInvalidas()
        usuario.registrar_exito()
        self.usuario_repository.actualizar(usuario)
        return self._emitir_tokens(usuario, familia_id=uuid4().hex)

    def renovar(self, refresh_token: str) -> ResultadoAuth:
        ahora = datetime.now(timezone.utc)
        guardado = self.refresh_repository.obtener_por_hash(
            hashear_refresh_token(refresh_token)
        )
        if guardado is None:
            raise TokenInvalido()
        if guardado.revocado_en is not None:    # reutilización
            self.refresh_repository.revocar_familia(guardado.familia_id)
            raise TokenInvalido()
        if not guardado.esta_vigente(ahora):
            raise TokenInvalido()
        usuario = self.usuario_repository.obtener_por_id(guardado.usuario_id)
        if usuario is None or not usuario.activo:
            raise TokenInvalido()
        token, registro = self._crear_refresh(usuario.id, guardado.familia_id)
        self.refresh_repository.rotar(guardado, registro)
        return ResultadoAuth(usuario, self._crear_access(usuario), token)

    def cerrar_sesion(self, refresh_token: str) -> None:
        guardado = self.refresh_repository.obtener_por_hash(
            hashear_refresh_token(refresh_token)
        )
        if guardado is not None:
            self.refresh_repository.revocar_familia(guardado.familia_id)

    def cerrar_todas_las_sesiones(self, usuario: Usuario) -> None:
        usuario.invalidar_sesiones()
        self.usuario_repository.actualizar(usuario)
        self.refresh_repository.revocar_todos_de_usuario(usuario.id)

    # Métodos internos para emitir tokens.
    def _crear_refresh(self, usuario_id: int, familia_id: str):
        token = generar_refresh_token()
        registro = RefreshToken(
            usuario_id=usuario_id,
            token_hash=hashear_refresh_token(token),
            familia_id=familia_id,
            expira_en=datetime.now(timezone.utc)
            + timedelta(days=config.REFRESH_TOKEN_DIAS),
        )
        return token, registro

    def _crear_access(self, usuario: Usuario) -> str:
        return self.jwt_service.crear_access_token(usuario.id, usuario.token_version)

    def _emitir_tokens(self, usuario: Usuario, familia_id: str) -> ResultadoAuth:
        token, registro = self._crear_refresh(usuario.id, familia_id)
        self.refresh_repository.crear(registro)
        return ResultadoAuth(usuario, self._crear_access(usuario), token)
