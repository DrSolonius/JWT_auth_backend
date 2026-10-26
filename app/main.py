from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

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
from infrastructure.seeders.curso_seeder import seed_cursos
from infrastructure.seeders.estudiante_seeder import seed_estudiantes
from infrastructure.seeders.inscripcion_seeder import seed_inscripciones
from presentation.routers.curso_router import router as curso_router
from presentation.routers.estudiante_router import router
from presentation.routers.inscripcion_router import (
    router as inscripcion_router,
)


def cargar_datos_iniciales() -> None:
    with SessionLocal() as session:
        estudiante_repository = EstudianteRepository(session)
        curso_repository = CursoRepository(session)
        inscripcion_repository = InscripcionRepository(session)

        # Solo cargamos datos si la base de datos está vacía.
        if estudiante_repository.contar() > 0:
            return

        seed_estudiantes(
            EstudianteService(estudiante_repository, inscripcion_repository)
        )
        seed_cursos(CursoService(curso_repository, inscripcion_repository))
        seed_inscripciones(
            InscripcionService(
                inscripcion_repository,
                estudiante_repository,
                curso_repository,
            )
        )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Las tablas las crea Alembic (uv run alembic upgrade head).
    cargar_datos_iniciales()
    yield


app = FastAPI(title="Sistema Académico", lifespan=lifespan)

app.include_router(router)
app.include_router(curso_router)
app.include_router(inscripcion_router)
