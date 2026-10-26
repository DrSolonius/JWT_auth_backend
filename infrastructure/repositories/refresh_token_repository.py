from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from domain.refresh_token import RefreshToken
from infrastructure.mappers import refresh_token_mapper
from infrastructure.models.refresh_token_model import RefreshTokenModel


class RefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, token: RefreshToken) -> RefreshToken:
        modelo = refresh_token_mapper.a_modelo(token)

        self.session.add(modelo)
        self.session.commit()
        self.session.refresh(modelo)

        return refresh_token_mapper.a_dominio(modelo)

    def obtener_por_hash(self, token_hash: str) -> RefreshToken | None:
        modelo = self.session.scalars(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token_hash == token_hash
            )
        ).first()

        if modelo is None:
            return None

        return refresh_token_mapper.a_dominio(modelo)

    def rotar(self, actual: RefreshToken, nuevo: RefreshToken) -> None:
        """Revoca el token actual y guarda el nuevo en un solo commit."""
        modelo = self.session.get(RefreshTokenModel, actual.id)
        modelo.revocado_en = datetime.now(timezone.utc)
        self.session.add(refresh_token_mapper.a_modelo(nuevo))
        self.session.commit()

    def revocar_familia(self, familia_id: str) -> None:
        self.session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.familia_id == familia_id,
                RefreshTokenModel.revocado_en.is_(None),
            )
            .values(revocado_en=datetime.now(timezone.utc))
        )
        self.session.commit()

    def revocar_todos_de_usuario(self, usuario_id: int) -> None:
        self.session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.usuario_id == usuario_id,
                RefreshTokenModel.revocado_en.is_(None),
            )
            .values(revocado_en=datetime.now(timezone.utc))
        )
        self.session.commit()
