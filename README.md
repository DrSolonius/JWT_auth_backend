# Sistema Académico — API de estudiantes y cursos

Proyecto educativo para aprender a construir una API HTTP con **FastAPI**, organizar el código por capas y persistir datos en **PostgreSQL** usando el ORM **SQLAlchemy 2.1** y migraciones con **Alembic**.

La aplicación permite:

- crear, consultar, actualizar, eliminar y listar **estudiantes** y **cursos** con paginación;
- **inscribir** estudiantes en cursos: un estudiante puede tomar n cursos y un curso puede tener n estudiantes (relación **muchos a muchos**).

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.14 | Lenguaje |
| FastAPI + Uvicorn | API HTTP y servidor |
| Pydantic | DTO y validación |
| SQLAlchemy 2.1 | ORM (modelos, sesiones, consultas) |
| psycopg2 | Driver de PostgreSQL |
| PostgreSQL | Base de datos |
| Alembic | Migraciones del esquema |
| python-dotenv | Lectura de la configuración desde `.env` |
| uv | Gestión de dependencias y entorno virtual |

---

## Requisitos

- Python 3.14 o superior.
- `uv` instalado.
- Git.
- PostgreSQL corriendo localmente, con una base de datos creada para el proyecto.

---

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/DrSolonius/backend_S4.git
cd backend_S4
```

Instala las dependencias:

```bash
uv sync
```

Configura la conexión a PostgreSQL copiando `.env.example` como `.env` y completando tus datos:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=clase
DB_USER=alumno
DB_PASSWORD=mi_clave_segura
```

El archivo `.env` contiene credenciales: está en `.gitignore` y **no se sube al repositorio**.

Crea las tablas aplicando las migraciones:

```bash
uv run alembic upgrade head
```

---

## Ejecutar la API

Desde la raíz del proyecto:

```bash
uv run uvicorn app.main:app --reload
```

Al iniciar, si la base de datos está vacía, los seeders cargan datos de prueba.

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Si el puerto está ocupado, puedes utilizar otro:

```bash
uv run uvicorn app.main:app --reload --port 8765
```

---

## Estructura del proyecto

```text
backend_S4/
├── .vscode/
│   ├── launch.json
│   └── settings.json
│
├── app/
│   └── main.py
│
├── application/
│   └── services/
│       ├── curso_service.py
│       ├── estudiante_service.py
│       └── inscripcion_service.py
│
├── domain/
│   ├── curso.py
│   ├── estudiante.py
│   └── inscripcion.py
│
├── infrastructure/
│   ├── database.py
│   │
│   ├── mappers/
│   │   ├── curso_mapper.py
│   │   └── estudiante_mapper.py
│   │
│   ├── models/
│   │   ├── curso_model.py
│   │   ├── estudiante_model.py
│   │   └── inscripcion_model.py
│   │
│   ├── repositories/
│   │   ├── curso_repository.py
│   │   ├── estudiante_repository.py
│   │   └── inscripcion_repository.py
│   │
│   └── seeders/
│       ├── curso_seeder.py
│       ├── estudiante_seeder.py
│       └── inscripcion_seeder.py
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_crear_tablas.py
│
├── presentation/
│   ├── dependencies.py
│   │
│   ├── routers/
│   │   ├── curso_router.py
│   │   ├── estudiante_router.py
│   │   └── inscripcion_router.py
│   │
│   └── schemas/
│       └── dtos/
│           ├── curso_dto.py
│           ├── curso_query_dto.py
│           ├── estudiante_dto.py
│           └── estudiante_query_dto.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Responsabilidad de cada capa

| Componente | Responsabilidad |
|---|---|
| `app/main.py` | Crea la aplicación FastAPI, carga los datos iniciales y registra los routers. |
| `presentation/routers` | Define los endpoints y recibe las solicitudes HTTP. |
| `presentation/schemas/dtos` | Contiene los DTO implementados con Pydantic. |
| `presentation/dependencies.py` | Abre una sesión de base de datos por solicitud y construye los servicios con `Depends`. |
| `application/services` | Coordina los casos de uso y las reglas de aplicación. |
| `domain` | Define las entidades `Estudiante`, `Curso` e `Inscripcion`, su estado y comportamiento. |
| `infrastructure/database.py` | Lee el `.env`, crea el `engine` de PostgreSQL, la `SessionLocal` y la clase `Base`. |
| `infrastructure/models` | Modelos ORM: las tablas de la base de datos como clases de Python. |
| `infrastructure/mappers` | Convierten entre entidades de dominio y modelos ORM. |
| `infrastructure/repositories` | Guardan y recuperan datos usando una sesión de SQLAlchemy. |
| `infrastructure/seeders` | Cargan datos iniciales para pruebas. |
| `migrations` | Migraciones de Alembic que crean y modifican el esquema. |

---

## Arquitectura

```text
CLIENTE
   │
   │ HTTP / JSON
   ▼
┌─────────────────────────────────┐
│ PRESENTATION                    │
│                                 │
│ Routers + DTO / Pydantic        │
│ Depends → sesión por solicitud  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ APPLICATION                     │
│                                 │
│ EstudianteService               │
│ CursoService                    │
│ InscripcionService              │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ DOMAIN                          │
│                                 │
│ Estudiante, Curso, Inscripcion  │
│ Estado y comportamiento         │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ INFRASTRUCTURE                  │
│                                 │
│ Repositories → Mappers          │
│ Modelos ORM → Session           │
└────────────────┬────────────────┘
                 │ SQL (psycopg2)
                 ▼
            PostgreSQL
```

Flujo simplificado:

```text
Cliente
   ↓
HTTP / JSON
   ↓
Router + DTO Pydantic
   ↓
Service
   ↓
Entidad de dominio
   ↓
Repository + Mapper
   ↓
Modelo ORM + Session (SQLAlchemy)
   ↓
PostgreSQL
```

El dominio y los servicios no conocen SQLAlchemy: trabajan con entidades de dominio. Solo la capa de infraestructura sabe que los datos viven en PostgreSQL.

---

## Modelo de datos

```text
┌──────────────┐        ┌─────────────────┐        ┌──────────────┐
│ estudiantes  │        │  inscripciones  │        │    cursos    │
├──────────────┤        ├─────────────────┤        ├──────────────┤
│ id (PK)      │1      n│ estudiante_id   │n      1│ id (PK)      │
│ nombre       ├────────┤   (PK, FK)      ├────────┤ codigo (UQ)  │
│ apellido     │        │ curso_id        │        │ nombre       │
│ email (UQ)   │        │   (PK, FK)      │        │ creditos     │
│ activo       │        └─────────────────┘        │ activo       │
└──────────────┘                                   └──────────────┘
```

- `inscripciones` es la **tabla de asociación** de la relación muchos a muchos.
- Su clave primaria es el par (`estudiante_id`, `curso_id`): un estudiante no puede inscribirse dos veces en el mismo curso.
- Las claves foráneas usan `ON DELETE CASCADE`: al eliminar un estudiante o un curso, se eliminan sus inscripciones.
- `email` y `codigo` son únicos.

En SQLAlchemy la relación se declara con `relationship(secondary=...)`:

```python
class EstudianteModel(Base):
    __tablename__ = "estudiantes"
    ...
    cursos: Mapped[list["CursoModel"]] = relationship(
        secondary=inscripciones,
        back_populates="estudiantes",
    )
```

---

## Endpoints disponibles

### Estudiantes

| Método | Endpoint | Acción |
|---|---|---|
| `POST` | `/estudiantes` | Crear estudiante |
| `GET` | `/estudiantes` | Listar estudiantes con paginación |
| `GET` | `/estudiantes/{estudiante_id}` | Obtener estudiante |
| `PUT` | `/estudiantes/{estudiante_id}` | Actualizar estudiante |
| `DELETE` | `/estudiantes/{estudiante_id}` | Eliminar estudiante (y sus inscripciones) |

### Cursos

| Método | Endpoint | Acción |
|---|---|---|
| `POST` | `/cursos` | Crear curso |
| `GET` | `/cursos` | Listar cursos con paginación |
| `GET` | `/cursos/{curso_id}` | Obtener curso |
| `PUT` | `/cursos/{curso_id}` | Actualizar curso |
| `DELETE` | `/cursos/{curso_id}` | Eliminar curso (y sus inscripciones) |

### Inscripciones

| Método | Endpoint | Acción |
|---|---|---|
| `POST` | `/estudiantes/{estudiante_id}/cursos/{curso_id}` | Inscribir al estudiante en el curso |
| `DELETE` | `/estudiantes/{estudiante_id}/cursos/{curso_id}` | Retirar al estudiante del curso |
| `GET` | `/estudiantes/{estudiante_id}/cursos` | Listar los cursos de un estudiante |
| `GET` | `/cursos/{curso_id}/estudiantes` | Listar los estudiantes de un curso |

Reglas de inscripción:

- el estudiante y el curso deben existir (si no, `404`);
- ambos deben estar activos (si no, `400`);
- no se puede inscribir dos veces en el mismo curso (`400`).

---

## Entidades de dominio

| Entidad | Atributos | Reglas |
|---|---|---|
| `Estudiante` | `id`, `nombre`, `apellido`, `email`, `activo` | Nombre, apellido y email obligatorios. Email único (sin distinguir mayúsculas). Propiedad `nombre_completo`. |
| `Curso` | `id`, `codigo`, `nombre`, `creditos`, `activo` | Código obligatorio, se guarda en mayúsculas y es único. Créditos ≥ 1. Propiedad `descripcion`. |
| `Inscripcion` | `estudiante_id`, `curso_id` | Une un estudiante con un curso. |

---

## ¿Qué es un DTO?

DTO significa **Data Transfer Object**: representa los datos que entran y salen de la API. En este proyecto los DTO son clases de Pydantic, por lo que además validan y serializan.

| DTO | Responsabilidad |
|---|---|
| `EstudianteCreateDTO` / `EstudianteUpdateDTO` | Validan los datos para crear o actualizar un estudiante. |
| `EstudianteResponseDTO` | Estructura de un estudiante devuelto por la API. |
| `EstudiantePaginaDTO` | Respuesta paginada de estudiantes. |
| `EstudianteQueryDTO` | Valida `pagina` y `tamano`. |
| `CursoCreateDTO` / `CursoUpdateDTO` | Validan los datos para crear o actualizar un curso (`creditos` entre 1 y 30). |
| `CursoResponseDTO` | Estructura de un curso devuelto por la API. |
| `CursoPaginaDTO` | Respuesta paginada de cursos. |
| `CursoQueryDTO` | Valida `pagina` y `tamano`. |

Ejemplo:

```python
class CursoCreateDTO(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    codigo: str = Field(min_length=1, max_length=20)
    nombre: str = Field(min_length=1, max_length=150)
    creditos: int = Field(ge=1, le=30)
```

### DTO, entidad de dominio y modelo ORM

```text
CursoCreateDTO      → frontera de la API (Pydantic)
        ↓
Curso               → dominio (dataclass, reglas de negocio)
        ↓  curso_mapper
CursoModel          → infraestructura (SQLAlchemy, tabla cursos)
        ↓
PostgreSQL
```

---

## Paginación

```python
class EstudianteQueryDTO(BaseModel):
    pagina: int = Field(default=1, ge=1)
    tamano: int = Field(default=10, ge=1, le=100)
```

El servicio calcula:

```python
offset = (pagina - 1) * tamano
```

y el repositorio lo traduce a SQL con SQLAlchemy:

```python
select(EstudianteModel)
    .order_by(EstudianteModel.id)
    .offset(offset)
    .limit(limite)
```

Con 60 estudiantes y `tamano=10`, la página 6 trae los registros 51 al 60 y la página 7 una lista vacía.

---

## Persistencia con SQLAlchemy 2.1

### Conexión (`infrastructure/database.py`)

```python
load_dotenv()

url = URL.create(
    "postgresql+psycopg2",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ.get("DB_PORT", 5432)),
    database=os.environ["DB_NAME"],
)

engine = create_engine(url, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
```

Cambia `echo=False` por `echo=True` para ver en consola el SQL que genera el ORM.

### Sesión por solicitud (`presentation/dependencies.py`)

Cada solicitud HTTP recibe su propia sesión, que se cierra al terminar:

```python
def get_session() -> Iterator[Session]:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
```

Los routers piden el servicio con `Depends`, y el servicio recibe repositorios que usan esa sesión:

```python
ServiceDep = Annotated[CursoService, Depends(get_curso_service)]


@router.get("/{curso_id}", response_model=CursoResponseDTO)
def obtener_curso(curso_id: CursoId, service: ServiceDep):
    ...
```

### Repositorios y mappers

Los repositorios mantienen los mismos métodos que cuando los datos estaban en memoria (`crear`, `obtener_por_id`, `listar`, `contar`, `actualizar`, `eliminar`), por eso los servicios y el dominio no cambiaron al incorporar el ORM. Internamente usan la sesión y un mapper:

```python
def crear(self, curso: Curso) -> Curso:
    modelo = curso_mapper.a_modelo(curso)

    self.session.add(modelo)
    self.session.commit()
    self.session.refresh(modelo)

    return curso_mapper.a_dominio(modelo)
```

---

## Migraciones con Alembic

Las tablas **no** se crean al iniciar la API: se crean y modifican con migraciones. Alembic guarda en la tabla `alembic_version` qué migración está aplicada. `migrations/env.py` usa el mismo `engine` que la aplicación, así que también lee la conexión desde el `.env` (no hay credenciales en `alembic.ini`).

| Comando | Qué hace |
|---|---|
| `uv run alembic upgrade head` | Aplica todas las migraciones pendientes. |
| `uv run alembic downgrade -1` | Deshace la última migración. |
| `uv run alembic downgrade base` | Deshace todas las migraciones (borra las tablas). |
| `uv run alembic current` | Muestra la migración aplicada. |
| `uv run alembic history` | Lista todas las migraciones. |
| `uv run alembic revision --autogenerate -m "mensaje"` | Crea una migración comparando los modelos con la base de datos. |
| `uv run alembic check` | Indica si hay cambios en los modelos sin migración. |

La migración inicial `0001_crear_tablas.py` crea `estudiantes`, `cursos` e `inscripciones` con sus índices únicos y claves foráneas.

Flujo para cambiar un modelo (por ejemplo, agregar una columna):

```text
1. Modificar el modelo en infrastructure/models/
2. uv run alembic revision --autogenerate -m "agregar columna telefono"
3. Revisar el archivo generado en migrations/versions/
4. uv run alembic upgrade head
```

Para empezar de cero:

```bash
uv run alembic downgrade base
uv run alembic upgrade head
```

---

## Seeders

Al iniciar la API, `app/main.py` revisa si la tabla `estudiantes` está vacía. Si lo está, carga:

| Seeder | Datos |
|---|---|
| `estudiante_seeder.py` | 60 estudiantes |
| `curso_seeder.py` | 10 cursos (`INF101`, `INF102`, …, `MAT102`) |
| `inscripcion_seeder.py` | 180 inscripciones (cada estudiante en 3 cursos) |

Si la base de datos ya tiene datos, los seeders no se ejecutan.

---

## Recorrido de una solicitud POST

```http
POST /estudiantes/1/cursos/5
```

```text
Cliente
   │ POST /estudiantes/1/cursos/5
   ▼
FastAPI
   │ valida los parámetros de ruta (> 0)
   │ get_session() abre una sesión
   ▼
inscripcion_router
   ▼
InscripcionService
   │ verifica que el estudiante y el curso existan y estén activos
   │ verifica que no exista la inscripción
   ▼
InscripcionRepository
   │ estudiante.cursos.append(curso)
   │ session.commit() → INSERT INTO inscripciones
   ▼
PostgreSQL
   ▼
CursoResponseDTO
   │ JSON + HTTP 201
   ▼
Cliente
   (la sesión se cierra)
```

---

## Probar la API con Swagger

Abre `http://127.0.0.1:8000/docs` y prueba:

```http
GET /estudiantes?pagina=1&tamano=10
GET /cursos
GET /estudiantes/1/cursos
POST /estudiantes/1/cursos/5
GET /cursos/5/estudiantes
```

Respuesta paginada:

```json
{
  "items": [
    {
      "id": 1,
      "codigo": "INF101",
      "nombre": "Introducción a la Programación",
      "creditos": 6,
      "activo": true,
      "descripcion": "INF101 - Introducción a la Programación"
    }
  ],
  "total": 10,
  "pagina": 1,
  "tamano": 10
}
```

---

## Códigos HTTP importantes

| Código | Significado |
|---|---|
| `200 OK` | Solicitud procesada correctamente |
| `201 Created` | Recurso creado o inscripción realizada |
| `204 No Content` | Recurso eliminado o estudiante retirado del curso |
| `400 Bad Request` | Regla de aplicación inválida (email o código duplicado, inscripción repetida, entidad inactiva) |
| `404 Not Found` | Estudiante, curso o inscripción inexistente |
| `422 Unprocessable Entity` | Error de validación |

---

## Depuración con VS Code

El proyecto incluye `.vscode/launch.json`. Para iniciar la depuración:

```text
Ctrl + Shift + D → "Depurar API de estudiantes" → F5
```

La configuración utiliza el puerto `8001`. Si ese puerto está ocupado, cambia el valor en `.vscode/launch.json`.

| Tecla | Acción |
|---|---|
| `F9` | Agregar o quitar breakpoint |
| `F10` | Avanzar sin entrar en una función |
| `F11` | Entrar en una función |
| `Shift + F11` | Salir de una función |
| `F5` | Continuar ejecución |
| `Shift + F5` | Detener depuración |

Referencia: [Depuración de Python en VS Code](https://code.visualstudio.com/docs/python/debugging).

---

## Problemas frecuentes

### KeyError: 'DB_USER' (u otra variable `DB_*`)

Falta el archivo `.env` o le falta esa variable. Copia `.env.example` como `.env` y completa los datos.

### relation "estudiantes" does not exist

Las tablas no existen todavía. Ejecuta:

```bash
uv run alembic upgrade head
```

### DuplicateTable al ejecutar `alembic upgrade head`

Las tablas ya existían antes de usar Alembic (por ejemplo, creadas con `create_all`). Marca la base de datos como actualizada sin volver a crearlas:

```bash
uv run alembic stamp head
```

### Address already in use

El puerto ya está siendo utilizado. Inicia Uvicorn en otro puerto:

```bash
uv run uvicorn app.main:app --reload --port 8765
```

### No module named 'app'

Ejecuta los comandos desde la carpeta `backend_S4/`.

---

## Estado actual del proyecto

Actualmente se trabajan:

- FastAPI, Uvicorn, HTTP y JSON.
- CRUD, rutas, parámetros de ruta y de consulta.
- Pydantic, schemas, DTO y validaciones.
- Entidades de dominio, servicios y repositorios.
- Relación muchos a muchos (estudiantes ↔ cursos).
- PostgreSQL con SQLAlchemy 2.1 (modelos, sesiones, relaciones).
- Mappers entre dominio y modelos ORM.
- Inyección de dependencias con `Depends`.
- Migraciones con Alembic.
- Configuración con `.env`.
- Seeders y paginación.
- Códigos de estado HTTP.
- Swagger / OpenAPI.
- Separación de responsabilidades.

Todavía no se incorporan:

- Pruebas automatizadas.
- Autenticación.
- Autorización.
- Docker.
- CI/CD.

El proyecto continuará evolucionando progresivamente durante el curso.
