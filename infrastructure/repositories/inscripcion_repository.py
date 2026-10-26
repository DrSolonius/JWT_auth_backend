from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from domain.inscripcion import Inscripcion
from infrastructure.models.curso_model import CursoModel
from infrastructure.models.estudiante_model import EstudianteModel
from infrastructure.models.inscripcion_model import inscripciones


class InscripcionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, inscripcion: Inscripcion) -> Inscripcion:
        estudiante = self.session.get(
            EstudianteModel, inscripcion.estudiante_id
        )
        curso = self.session.get(CursoModel, inscripcion.curso_id)

        # Al agregar el curso a la relación, SQLAlchemy inserta
        # la fila correspondiente en la tabla de asociación.
        estudiante.cursos.append(curso)
        self.session.commit()

        return inscripcion

    def existe(self, inscripcion: Inscripcion) -> bool:
        fila = self.session.execute(
            select(inscripciones).where(
                inscripciones.c.estudiante_id == inscripcion.estudiante_id,
                inscripciones.c.curso_id == inscripcion.curso_id,
            )
        ).first()

        return fila is not None

    def eliminar(self, inscripcion: Inscripcion) -> bool:
        resultado = self.session.execute(
            delete(inscripciones).where(
                inscripciones.c.estudiante_id == inscripcion.estudiante_id,
                inscripciones.c.curso_id == inscripcion.curso_id,
            )
        )
        self.session.commit()

        return resultado.rowcount > 0

    def listar_cursos_ids(self, estudiante_id: int) -> list[int]:
        return list(
            self.session.scalars(
                select(inscripciones.c.curso_id)
                .where(inscripciones.c.estudiante_id == estudiante_id)
                .order_by(inscripciones.c.curso_id)
            )
        )

    def listar_estudiantes_ids(self, curso_id: int) -> list[int]:
        return list(
            self.session.scalars(
                select(inscripciones.c.estudiante_id)
                .where(inscripciones.c.curso_id == curso_id)
                .order_by(inscripciones.c.estudiante_id)
            )
        )

    def eliminar_por_estudiante(self, estudiante_id: int) -> None:
        self.session.execute(
            delete(inscripciones).where(
                inscripciones.c.estudiante_id == estudiante_id
            )
        )
        self.session.commit()

    def eliminar_por_curso(self, curso_id: int) -> None:
        self.session.execute(
            delete(inscripciones).where(inscripciones.c.curso_id == curso_id)
        )
        self.session.commit()
