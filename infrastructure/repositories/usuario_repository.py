from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.usuario import Usuario
from infrastructure.mappers import usuario_mapper
from infrastructure.models.usuario_model import UsuarioModel


class UsuarioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, usuario: Usuario) -> Usuario:
        modelo = usuario_mapper.a_modelo(usuario)

        self.session.add(modelo)

        try:
            self.session.commit()
        except IntegrityError as error:
            # Dos registros simultáneos con el mismo email: el índice único lo frena.
            self.session.rollback()
            raise ValueError("No se pudo completar el registro.") from error

        self.session.refresh(modelo)

        return usuario_mapper.a_dominio(modelo)

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        modelo = self.session.get(UsuarioModel, usuario_id)

        if modelo is None:
            return None

        return usuario_mapper.a_dominio(modelo)

    def obtener_por_email(self, email: str) -> Usuario | None:
        email_buscado = email.strip().lower()

        modelo = self.session.scalars(
            select(UsuarioModel).where(
                func.lower(UsuarioModel.email) == email_buscado
            )
        ).first()

        if modelo is None:
            return None

        return usuario_mapper.a_dominio(modelo)

    def actualizar(self, usuario: Usuario) -> Usuario:
        modelo = self.session.get(UsuarioModel, usuario.id)

        if modelo is None:
            raise ValueError("El usuario no existe.")

        usuario_mapper.actualizar_modelo(modelo, usuario)
        self.session.commit()
        self.session.refresh(modelo)

        return usuario_mapper.a_dominio(modelo)
