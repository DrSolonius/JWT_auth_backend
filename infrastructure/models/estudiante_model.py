from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base
from infrastructure.models.inscripcion_model import inscripciones


class EstudianteModel(Base):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    cursos: Mapped[list["CursoModel"]] = relationship(  # noqa: F821
        secondary=inscripciones,
        back_populates="estudiantes",
    )
