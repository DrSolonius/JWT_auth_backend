from pydantic import BaseModel, ConfigDict, Field


class EstudianteCreateDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=254)


class EstudianteUpdateDTO(EstudianteCreateDTO):
    """Para actualizar se requieren los tres campos."""

    pass


class EstudianteResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    email: str
    activo: bool
    nombre_completo: str


class EstudiantePaginaDTO(BaseModel):
    items: list[EstudianteResponseDTO]
    total: int
    pagina: int
    tamano: int