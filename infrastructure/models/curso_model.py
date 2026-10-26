from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base
from infrastructure.models.estudiante_model import EstudianteModel
from infrastructure.models.inscripcion_model import inscripciones


class CursoModel(Base):
    __tablename__ = "cursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    creditos: Mapped[int] = mapped_column(Integer)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    estudiantes: Mapped[list[EstudianteModel]] = relationship(
        secondary=inscripciones,
        back_populates="cursos",
    )
