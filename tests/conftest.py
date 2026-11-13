"""Fixtures compartidos por todos los niveles de prueba.

Los tests usan PostgreSQL, el mismo motor que la aplicación, pero en una base
APARTE: ``clase_test`` (la crea db-init/01-crear-base-de-pruebas.sh).
Las tablas se crean una vez con Alembic y, después de cada test, se vacían:
así ningún test depende del resultado de otro (independencia entre tests).
"""
import os

from dotenv import load_dotenv

# La base de pruebas se configura con variables TEST_DB_* propias, distintas de
# las DB_* de la aplicación: así un .env con DB_NAME=clase nunca se mezcla con
# los tests. Salen del entorno o del archivo .env (ver .env.example); en CI las
# define el workflow, y la contraseña viene de un secret de GitHub.
load_dotenv()

_VARIABLES = ("USER", "PASSWORD", "HOST", "PORT", "NAME")
_faltan = [f"TEST_DB_{v}" for v in _VARIABLES if not os.environ.get(f"TEST_DB_{v}")]
if _faltan:
    raise RuntimeError(
        "Faltan variables para la base de pruebas: " + ", ".join(_faltan)
        + ". Cópialas desde .env.example a tu .env (o defínelas en el entorno)."
    )

# infrastructure/database.py lee las DB_* al importarse: se fijan ANTES de
# importar la aplicación y reemplazan a las de la app.
for _v in _VARIABLES:
    os.environ[f"DB_{_v}"] = os.environ[f"TEST_DB_{_v}"]

# Valores que no son credenciales de ningún sistema real.
os.environ.setdefault("JWT_SECRET", "secreto-solo-para-tests-de-al-menos-32-bytes")
os.environ.setdefault("COOKIE_SECURE", "false")

# Seguro de vida: los tests borran datos. Nunca deben correr contra "clase".
if not os.environ["DB_NAME"].endswith("_test"):
    raise RuntimeError(
        f"TEST_DB_NAME={os.environ['DB_NAME']!r}: los tests solo corren contra una "
        "base cuyo nombre termine en '_test' (se vacía después de cada test)."
    )

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.main import app  # noqa: E402
from application.services.estudiante_service import EstudianteService  # noqa: E402
from domain.usuario import Usuario  # noqa: E402
from infrastructure.database import Base, engine  # noqa: E402
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


@pytest.fixture(scope="session", autouse=True)
def esquema():
    """Crea las tablas UNA vez por ejecución, con las mismas migraciones
    que usa producción (alembic upgrade head)."""
    command.upgrade(Config("alembic.ini"), "head")
    yield
    engine.dispose()


@pytest.fixture
def session(esquema) -> Session:
    """Sesión sobre clase_test. Al terminar el test se vacían las tablas
    y se reinician los ids, así cada test parte de una base vacía."""
    with sessionmaker(bind=engine, autoflush=False)() as session:
        yield session
        session.rollback()

    tablas = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    with engine.begin() as conexion:
        conexion.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))


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
