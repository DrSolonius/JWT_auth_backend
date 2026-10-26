from pydantic import BaseModel, Field
class EstudianteQueryDTO(BaseModel):
    pagina: int = Field(default=1, ge=1)
    tamano: int = Field(default=10, ge=1, le=100)