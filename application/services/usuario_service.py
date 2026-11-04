from domain.usuario import Usuario


class UsuarioService:
    def __init__(self, usuario_repository, refresh_repository) -> None:
        self.usuario_repository = usuario_repository
        self.refresh_repository = refresh_repository

    def listar(self, activo: bool | None = None) -> list[Usuario]:
        return self.usuario_repository.listar(activo)

    def activar(self, usuario_id: int) -> Usuario:
        usuario = self._obtener(usuario_id)
        usuario.activar()
        return self.usuario_repository.actualizar(usuario)

    def desactivar(self, usuario_id: int, admin_id: int) -> Usuario:
        # Sin esto, el único administrador podría dejar la API sin nadie que apruebe.
        if usuario_id == admin_id:
            raise ValueError("No puedes desactivar tu propia cuenta.")

        usuario = self._obtener(usuario_id)
        usuario.desactivar()
        usuario = self.usuario_repository.actualizar(usuario)
        self.refresh_repository.revocar_todos_de_usuario(usuario_id)
        return usuario

    def _obtener(self, usuario_id: int) -> Usuario:
        usuario = self.usuario_repository.obtener_por_id(usuario_id)

        if usuario is None:
            raise LookupError("El usuario no existe.")

        return usuario
