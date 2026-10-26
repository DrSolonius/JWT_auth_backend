from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from application.services.curso_service import CursoService
from application.services.estudiante_service import EstudianteService
from application.services.inscripcion_service import InscripcionService
from infrastructure.database import SessionLocal
from infrastructure.repositories.curso_repository import CursoRepository
from infrastructure.repositories.estudiante_repository import (
    EstudianteRepository,
)
from infrastructure.repositories.inscripcion_repository import (
    InscripcionRepository,
)


def get_session() -> Iterator[Session]:
    """Abre una sesión por solicitud y la cierra al terminar."""
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]


def get_estudiante_service(session: SessionDep) -> EstudianteService:
    return EstudianteService(
        EstudianteRepository(session),
        InscripcionRepository(session),
    )


def get_curso_service(session: SessionDep) -> CursoService:
    return CursoService(
        CursoRepository(session),
        InscripcionRepository(session),
    )


def get_inscripcion_service(session: SessionDep) -> InscripcionService:
    return InscripcionService(
        InscripcionRepository(session),
        EstudianteRepository(session),
        CursoRepository(session),
    )
