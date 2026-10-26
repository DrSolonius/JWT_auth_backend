from pydantic import BaseModel, ConfigDict, Field, SecretStr


class RegistroDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    email: str = Field(min_length=3, max_length=254)
    password: SecretStr = Field(min_length=4, max_length=128)


class LoginDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    email: str = Field(min_length=3, max_length=254)
    password: SecretStr = Field(min_length=1, max_length=128)


class UsuarioResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    activo: bool


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
