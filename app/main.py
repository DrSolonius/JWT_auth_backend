from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from infrastructure.repositories.usuario_repository import UsuarioRepository
from infrastructure.seeders.curso_seeder import seed_cursos
from infrastructure.seeders.estudiante_seeder import seed_estudiantes
from infrastructure.seeders.inscripcion_seeder import seed_inscripciones
from infrastructure.seeders.usuario_seeder import EMAIL_ADMIN, seed_usuarios
from presentation.dependencies import get_auth_service
from presentation.routers.auth_router import router as auth_router
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


def cargar_usuarios_iniciales() -> None:
    with SessionLocal() as session:
        # Función aparte: cargar_datos_iniciales sale si ya hay estudiantes.
        if UsuarioRepository(session).obtener_por_email(EMAIL_ADMIN):
            return

        seed_usuarios(get_auth_service(session))


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Las tablas las crea Alembic (uv run alembic upgrade head).
    cargar_datos_iniciales()
    cargar_usuarios_iniciales()
    yield


app = FastAPI(title="Sistema Académico", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # el frontend, explícito
    allow_credentials=True,  # permite enviar la cookie del refresh token
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(router)
app.include_router(curso_router)
app.include_router(inscripcion_router)
