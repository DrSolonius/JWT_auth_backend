from application.services.inscripcion_service import InscripcionService


def seed_inscripciones(service: InscripcionService) -> None:
    """Inscribe a cada estudiante de prueba en 3 de los 10 cursos."""

    for estudiante_id in range(1, 61):
        for desplazamiento in range(3):
            curso_id = (estudiante_id + desplazamiento - 1) % 10 + 1

            service.inscribir(
                estudiante_id=estudiante_id,
                curso_id=curso_id,
            )
