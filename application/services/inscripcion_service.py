from domain.curso import Curso
from domain.estudiante import Estudiante
from domain.inscripcion import Inscripcion
from infrastructure.repositories.curso_repository import CursoRepository
from infrastructure.repositories.estudiante_repository import (
    EstudianteRepository,
)
from infrastructure.repositories.inscripcion_repository import (
    InscripcionRepository,
)


class InscripcionService:
    def __init__(
        self,
        repository: InscripcionRepository,
        estudiante_repository: EstudianteRepository,
        curso_repository: CursoRepository,
    ) -> None:
        self.repository = repository
        self.estudiante_repository = estudiante_repository
        self.curso_repository = curso_repository

    def inscribir(self, estudiante_id: int, curso_id: int) -> Curso:
        estudiante = self._obtener_estudiante(estudiante_id)
        curso = self._obtener_curso(curso_id)

        if not estudiante.activo:
            raise ValueError("El estudiante no está activo.")

        if not curso.activo:
            raise ValueError("El curso no está activo.")

        inscripcion = Inscripcion(
            estudiante_id=estudiante_id,
            curso_id=curso_id,
        )

        if self.repository.existe(inscripcion):
            raise ValueError(
                "El estudiante ya está inscrito en ese curso."
            )

        self.repository.crear(inscripcion)

        return curso

    def retirar(self, estudiante_id: int, curso_id: int) -> bool:
        return self.repository.eliminar(
            Inscripcion(
                estudiante_id=estudiante_id,
                curso_id=curso_id,
            )
        )

    def cursos_de_estudiante(self, estudiante_id: int) -> list[Curso]:
        self._obtener_estudiante(estudiante_id)

        return [
            self._obtener_curso(curso_id)
            for curso_id in self.repository.listar_cursos_ids(estudiante_id)
        ]

    def estudiantes_de_curso(self, curso_id: int) -> list[Estudiante]:
        self._obtener_curso(curso_id)

        return [
            self._obtener_estudiante(estudiante_id)
            for estudiante_id in self.repository.listar_estudiantes_ids(
                curso_id
            )
        ]

    def _obtener_estudiante(self, estudiante_id: int) -> Estudiante:
        estudiante = self.estudiante_repository.obtener_por_id(estudiante_id)

        if estudiante is None:
            raise LookupError("El estudiante no existe.")

        return estudiante

    def _obtener_curso(self, curso_id: int) -> Curso:
        curso = self.curso_repository.obtener_por_id(curso_id)

        if curso is None:
            raise LookupError("El curso no existe.")

        return curso
