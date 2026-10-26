from sqlalchemy import Column, ForeignKey, Integer, Table

from infrastructure.database import Base


# Tabla de asociación para la relación muchos a muchos:
# un estudiante puede tomar n cursos y un curso puede tener n estudiantes.
inscripciones = Table(
    "inscripciones",
    Base.metadata,
    Column(
        "estudiante_id",
        Integer,
        ForeignKey("estudiantes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "curso_id",
        Integer,
        ForeignKey("cursos.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
