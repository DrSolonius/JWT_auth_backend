from domain.usuario import Usuario
from infrastructure.models.usuario_model import UsuarioModel


def a_dominio(modelo: UsuarioModel) -> Usuario:
    return Usuario(
        id=modelo.id,
        email=modelo.email,
        password_hash=modelo.password_hash,
        activo=modelo.activo,
        token_version=modelo.token_version,
        intentos_fallidos=modelo.intentos_fallidos,
        bloqueado_hasta=modelo.bloqueado_hasta,
    )


def a_modelo(usuario: Usuario) -> UsuarioModel:
    return UsuarioModel(
        id=usuario.id,
        email=usuario.email,
        password_hash=usuario.password_hash,
        activo=usuario.activo,
        token_version=usuario.token_version,
        intentos_fallidos=usuario.intentos_fallidos,
        bloqueado_hasta=usuario.bloqueado_hasta,
    )


def actualizar_modelo(modelo: UsuarioModel, usuario: Usuario) -> None:
    modelo.email = usuario.email
    modelo.password_hash = usuario.password_hash
    modelo.activo = usuario.activo
    modelo.token_version = usuario.token_version
    modelo.intentos_fallidos = usuario.intentos_fallidos
    modelo.bloqueado_hasta = usuario.bloqueado_hasta
