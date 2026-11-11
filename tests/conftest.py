"""Fixtures compartidos por todos los niveles de prueba.

El sistema usa PostgreSQL, pero los tests NO tocan esa base: cada test
recibe una base SQLite en memoria, creada desde cero con los mismos modelos
de SQLAlchemy. Así los tests son rápidos, no necesitan Docker y ningún test
depende del resultado de otro (independencia entre tests).
"""
import os

# infrastructure/database.py y security/config.py leen estas variables al
# importarse. Deben existir ANTES de importar la aplicación.
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("JWT_SECRET", "secreto-solo-para-tests")
os.environ.setdefault("COOKIE_SECURE", "false")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.main import app  # noqa: E402
from application.services.estudiante_service import EstudianteService  # noqa: E402
from domain.usuario import Usuario  # noqa: E402
from infrastructure.database import Base  # noqa: E402
from infrastructure.repositories.estudiante_repository import (  # noqa: E402
    EstudianteRepository,
)
from infrastructure.repositories.inscripcion_repository import (  # noqa: E402
    InscripcionRepository,
)

# Importar los modelos registra las tablas en Base.metadata.
from infrastructure.models import (  # noqa: E402, F401
    curso_model,
    estudiante_model,
    inscripcion_model,
    refresh_token_model,
    usuario_model,
)
from presentation.dependencies import (  # noqa: E402
    get_session,
    get_usuario_actual,
)


@pytest.fixture
def session() -> Session:
    """Base de datos SQLite en memoria, NUEVA para cada test."""
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,  # una sola conexión: la base vive en memoria
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with sessionmaker(bind=engine, autoflush=False)() as session:
        yield session

    engine.dispose()


@pytest.fixture
def repository(session: Session) -> EstudianteRepository:
    return EstudianteRepository(session)


@pytest.fixture
def service(session: Session) -> EstudianteService:
    return EstudianteService(
        EstudianteRepository(session),
        InscripcionRepository(session),
    )


@pytest.fixture
def client_sin_login(session: Session):
    """Cliente HTTP sobre la app real: solo se reemplaza la sesión de BD."""
    app.dependency_overrides[get_session] = lambda: session

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def client(client_sin_login: TestClient) -> TestClient:
    """Igual que el anterior, pero con un usuario ya autenticado.

    Los tests de estudiantes no prueban el login: lo reemplazan.
    """
    app.dependency_overrides[get_usuario_actual] = lambda: Usuario(
        email="docente@example.com", password_hash="no-importa", id=1
    )

    return client_sin_login
