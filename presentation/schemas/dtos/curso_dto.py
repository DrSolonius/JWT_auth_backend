from pydantic import BaseModel, ConfigDict, Field


class CursoCreateDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    codigo: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1, max_length=150)
    creditos: int = Field(ge=1, le=30)


class CursoUpdateDTO(CursoCreateDTO):
    """Para actualizar se requieren los tres campos."""

    pass


class CursoResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    creditos: int
    activo: bool
    descripcion: str


class CursoPaginaDTO(BaseModel):
    items: list[CursoResponseDTO]
    total: int
    pagina: int
    tamano: int
