from domain.curso import Curso
from infrastructure.repositories.curso_repository import (
    CursoRepository,
)
from infrastructure.repositories.inscripcion_repository import (
    InscripcionRepository,
)


class CursoService:
    def __init__(
        self,
        repository: CursoRepository,
        inscripcion_repository: InscripcionRepository,
    ) -> None:
        self.repository = repository
        self.inscripcion_repository = inscripcion_repository

    def crear(
        self,
        codigo: str,
        nombre: str,
        creditos: int,
    ) -> Curso:
        curso = Curso(
            codigo=codigo,
            nombre=nombre,
            creditos=creditos,
        )

        self._validar_codigo_disponible(curso.codigo)

        return self.repository.crear(curso)

    def obtener(self, curso_id: int) -> Curso | None:
        return self.repository.obtener_por_id(curso_id)

    def listar(
        self,
        pagina: int,
        tamano: int,
    ) -> tuple[list[Curso], int]:
        if pagina < 1:
            raise ValueError("La página debe ser mayor o igual a 1.")

        if tamano < 1 or tamano > 100:
            raise ValueError("El tamaño debe estar entre 1 y 100.")

        offset = (pagina - 1) * tamano

        cursos = self.repository.listar(
            offset=offset,
            limite=tamano,
        )
        total = self.repository.contar()

        return cursos, total

    def actualizar(
        self,
        curso_id: int,
        codigo: str,
        nombre: str,
        creditos: int,
    ) -> Curso | None:
        actual = self.repository.obtener_por_id(curso_id)

        if actual is None:
            return None

        actualizado = Curso(
            id=actual.id,
            codigo=codigo,
            nombre=nombre,
            creditos=creditos,
            activo=actual.activo,
        )

        self._validar_codigo_disponible(
            codigo=actualizado.codigo,
            curso_id=curso_id,
        )

        return self.repository.actualizar(actualizado)

    def eliminar(self, curso_id: int) -> bool:
        eliminado = self.repository.eliminar(curso_id)

        if eliminado:
            self.inscripcion_repository.eliminar_por_curso(curso_id)

        return eliminado

    def _validar_codigo_disponible(
        self,
        codigo: str,
        curso_id: int | None = None,
    ) -> None:
        existente = self.repository.obtener_por_codigo(codigo)

        if existente is not None and existente.id != curso_id:
            raise ValueError(
                "Ya existe un curso con ese código."
            )
