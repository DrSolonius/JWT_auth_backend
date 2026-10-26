from dataclasses import dataclass


@dataclass(frozen=True)
class Inscripcion:
    """Relación muchos a muchos: un estudiante puede tomar n cursos
    y un curso puede tener n estudiantes."""

    estudiante_id: int
    curso_id: int
