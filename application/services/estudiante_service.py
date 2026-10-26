from domain.estudiante import Estudiante
from infrastructure.repositories.estudiante_repository import (
    EstudianteRepository,
)
from infrastructure.repositories.inscripcion_repository import (
    InscripcionRepository,
)


class EstudianteService:
    def __init__(
        self,
        repository: EstudianteRepository,
        inscripcion_repository: InscripcionRepository,
    ) -> None:
        self.repository = repository
        self.inscripcion_repository = inscripcion_repository

    def crear(
        self,
        nombre: str,
        apellido: str,
        email: str,
    ) -> Estudiante:
        estudiante = Estudiante(
            nombre=nombre,
            apellido=apellido,
            email=email,
        )

        self._validar_email_disponible(estudiante.email)

        return self.repository.crear(estudiante)

    def obtener(self, estudiante_id: int) -> Estudiante | None:
        return self.repository.obtener_por_id(estudiante_id)

    def listar(
        self,
        pagina: int,
        tamano: int,
    ) -> tuple[list[Estudiante], int]:
        if pagina < 1:
            raise ValueError("La página debe ser mayor o igual a 1.")

        if tamano < 1 or tamano > 100:
            raise ValueError("El tamaño debe estar entre 1 y 100.")

        offset = (pagina - 1) * tamano

        estudiantes = self.repository.listar(
            offset=offset,
            limite=tamano,
        )
        total = self.repository.contar()

        return estudiantes, total

    def actualizar(
        self,
        estudiante_id: int,
        nombre: str,
        apellido: str,
        email: str,
    ) -> Estudiante | None:
        actual = self.repository.obtener_por_id(estudiante_id)

        if actual is None:
            return None

        actualizado = Estudiante(
            id=actual.id,
            nombre=nombre,
            apellido=apellido,
            email=email,
            activo=actual.activo,
        )

        self._validar_email_disponible(
            email=actualizado.email,
            estudiante_id=estudiante_id,
        )

        return self.repository.actualizar(actualizado)

    def eliminar(self, estudiante_id: int) -> bool:
        eliminado = self.repository.eliminar(estudiante_id)

        if eliminado:
            self.inscripcion_repository.eliminar_por_estudiante(estudiante_id)

        return eliminado

    def _validar_email_disponible(
        self,
        email: str,
        estudiante_id: int | None = None,
    ) -> None:
        existente = self.repository.obtener_por_email(email)

        if existente is not None and existente.id != estudiante_id:
            raise ValueError(
                "Ya existe un estudiante con ese email."
            )