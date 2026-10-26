from domain.refresh_token import RefreshToken
from infrastructure.models.refresh_token_model import RefreshTokenModel


def a_dominio(modelo: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        token_hash=modelo.token_hash,
        familia_id=modelo.familia_id,
        expira_en=modelo.expira_en,
        revocado_en=modelo.revocado_en,
    )


def a_modelo(token: RefreshToken) -> RefreshTokenModel:
    return RefreshTokenModel(
        id=token.id,
        usuario_id=token.usuario_id,
        token_hash=token.token_hash,
        familia_id=token.familia_id,
        expira_en=token.expira_en,
        revocado_en=token.revocado_en,
    )
