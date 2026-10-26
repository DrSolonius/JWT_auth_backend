import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Lee el archivo .env (busca en esta carpeta y en las superiores).
load_dotenv()

url = URL.create(
    "postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ.get("DB_PORT", 5432)),
    database=os.environ["DB_NAME"],
)

# echo=True imprime en consola el SQL que genera el ORM (útil para aprender).
engine = create_engine(url, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass

# Las tablas se crean con Alembic: uv run alembic upgrade head
