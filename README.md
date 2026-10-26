# Sistema Académico — API de estudiantes y cursos

Proyecto educativo para aprender a construir una API HTTP con **FastAPI**, organizar el código por capas y persistir datos en **PostgreSQL** usando el ORM **SQLAlchemy 2.1** y migraciones con **Alembic**.

La aplicación permite:

- crear, consultar, actualizar, eliminar y listar **estudiantes** y **cursos** con paginación;
- **inscribir** estudiantes en cursos: un estudiante puede tomar n cursos y un curso puede tener n estudiantes (relación **muchos a muchos**);
- **registrarse, iniciar sesión y cerrar sesión** con **JWT** (access token) y **refresh tokens** en una cookie segura. Todos los endpoints de estudiantes, cursos e inscripciones exigen un token.

El proyecto incluye un **`docker-compose.yml`** que levanta **dos contenedores**: la API (`sistema_academico_app`) y PostgreSQL (`sistema_academico_db`). Con `docker compose up --build` queda todo funcionando, sin instalar Python ni PostgreSQL en tu PC.

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.14 | Lenguaje |
| FastAPI + Uvicorn | API HTTP y servidor |
| Pydantic | DTO y validación |
| SQLAlchemy 2.1 | ORM (modelos, sesiones, consultas) |
| psycopg2 | Driver de PostgreSQL |
| PostgreSQL 17 | Base de datos |
| Alembic | Migraciones del esquema |
| python-dotenv | Lectura de la configuración desde `.env` |
| pwdlib[argon2] | Hash de contraseñas con Argon2id |
| PyJWT | Crear, firmar y validar los access tokens (JWT) |
| Docker + Docker Compose | Levantar la API y PostgreSQL con un solo comando |
| uv | Gestión de dependencias y entorno virtual |

---

## Requisitos

- Docker Desktop (recomendado), **o** Python 3.14 + `uv` + un PostgreSQL local.
- Git.

---

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/DrSolonius/JWT_auth_backend.git
cd JWT_auth_backend
```

Copia `.env.example` como `.env` y completa tus datos:

```text
DB_HOST=localhost
DB_PORT=5433
DB_NAME=clase
DB_USER=alumno
DB_PASSWORD=mi_clave_segura

JWT_SECRET=pega-aqui-tu-secreto
ACCESS_TOKEN_MINUTOS=15
REFRESH_TOKEN_DIAS=7
COOKIE_SECURE=false
```

Genera un `JWT_SECRET` propio (uno por persona y por entorno):

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

El archivo `.env` contiene credenciales y el secreto que firma los tokens: está en `.gitignore` y **no se sube al repositorio**. En `.env.example` el `JWT_SECRET` queda vacío a propósito.

---

## Docker Compose: un archivo, dos contenedores

`docker-compose.yml` define dos **servicios**. Al ejecutar `docker compose up --build`, Docker crea un contenedor por cada uno, más una red y un volumen:

```text
                 Tu PC
   ┌───────────────────────────────────────────────────────┐
   │  Navegador / Swagger          Alembic, psql, DBeaver   │
   │  http://localhost:8080        localhost:5433           │
   └──────────┬──────────────────────────────┬──────────────┘
              │ 8080 → 8000                  │ 5433 → 5432
   ┌──────────▼──────────────┐     ┌─────────▼───────────────┐
   │ servicio app            │     │ servicio db             │
   │ sistema_academico_app   │────▶│ sistema_academico_db    │
   │ FastAPI + Uvicorn       │ db: │ PostgreSQL 17           │
   │ (imagen del Dockerfile) │5432 │ (imagen postgres:17)    │
   └─────────────────────────┘     └─────────┬───────────────┘
        red interna de Docker                │
                                   ┌─────────▼───────────────┐
                                   │ volumen pgdata          │
                                   │ (los datos persisten)   │
                                   └─────────────────────────┘
```

| | Servicio `db` | Servicio `app` |
|---|---|---|
| **Contenedor** | `sistema_academico_db` | `sistema_academico_app` |
| **Imagen** | `postgres:17` (oficial, se descarga) | Se construye con el `Dockerfile` del proyecto |
| **Puerto en tu PC → contenedor** | `5433 → 5432` (`DB_PORT_HOST`) | `8080 → 8000` (`APP_PORT`) |
| **Configuración** | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` desde el `.env` | `DB_*`, `JWT_SECRET`, `ACCESS_TOKEN_MINUTOS`, `REFRESH_TOKEN_DIAS`, `COOKIE_SECURE` desde el `.env` |
| **Datos** | Volumen `pgdata`: sobreviven a `docker compose down` | No guarda datos: todo va a la base |
| **Al arrancar** | `healthcheck` con `pg_isready` cada 5 segundos | Espera a que `db` esté sano (`depends_on: condition: service_healthy`), ejecuta `alembic upgrade head` y levanta Uvicorn |

Cómo se conectan:

- **La API habla con la base por la red interna de Docker.** Ahí la base se llama `db` y escucha en el 5432, por eso el compose le pasa `DB_HOST: db` y `DB_PORT: 5432` a la API, aunque tu `.env` diga `localhost` y `5433`.
- **Desde tu PC entras por los puertos publicados:** `localhost:8080` para la API y `localhost:5433` para la base. Se usa el 5433 para no chocar con un PostgreSQL instalado localmente en el 5432.
- **El `.env` no entra a la imagen** (está en `.dockerignore`): compose lo lee al arrancar y reemplaza cada `${VARIABLE}` antes de crear los contenedores. Si falta `JWT_SECRET`, se detiene con `Falta JWT_SECRET en el archivo .env`.

El `Dockerfile` construye la imagen de la API en **dos etapas**:

1. **builder**: parte de la imagen de `uv` con Python 3.14, instala las herramientas para compilar `psycopg2` y ejecuta `uv sync --frozen --no-dev` a partir de `uv.lock`.
2. **imagen final**: parte de `python:3.14-slim`, instala solo `libpq5`, copia el entorno virtual ya armado y el código. Así la imagen final no lleva compiladores.

Comandos útiles:

| Comando | Qué hace |
|---|---|
| `docker compose up --build` | Construye la imagen de la API y levanta los dos contenedores. |
| `docker compose up -d` | Levanta los contenedores en segundo plano, sin reconstruir. |
| `docker compose up -d --build` | Reconstruye la imagen: necesario después de cambiar código, dependencias o migraciones. |
| `docker compose up -d db` | Levanta solo la base de datos (para correr la API o Alembic desde tu PC). |
| `docker compose ps` | Muestra los dos contenedores y su estado. |
| `docker compose logs -f app` | Muestra los logs de la API. |
| `docker compose exec db psql -U alumno -d clase` | Abre una consola de PostgreSQL dentro del contenedor `db`. |
| `docker compose down` | Detiene y elimina los contenedores y la red (los datos se conservan en el volumen). |
| `docker compose down -v` | Igual, pero borra también el volumen con los datos de PostgreSQL. |

Todos los comandos se ejecutan desde la carpeta que tiene `docker-compose.yml`.

---

## Ejecutar la API

### Opción 1: con Docker (recomendada)

```bash
docker compose up --build
```

Levanta los dos contenedores, `sistema_academico_db` y `sistema_academico_app`, explicados en [Docker Compose: un archivo, dos contenedores](#docker-compose-un-archivo-dos-contenedores). Swagger queda en `http://localhost:8080/docs` y ReDoc en `http://localhost:8080/redoc`.

Para comprobar que ambos están corriendo:

```bash
docker compose ps
```

Debe mostrar `sistema_academico_app` como `Up` y `sistema_academico_db` como `Up (healthy)`.

### Opción 2: sin Docker

Instala las dependencias y aplica las migraciones contra tu PostgreSQL local (en el `.env`, `DB_PORT=5432`):

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Swagger queda en `http://127.0.0.1:8000/docs`. Si el puerto está ocupado:

```bash
uv run uvicorn app.main:app --reload --port 8765
```

También puedes correr la API en tu PC usando solo la base de datos de Docker: `docker compose up -d db` y `DB_PORT=5433` en el `.env`.

Al iniciar, si la base de datos está vacía, los seeders cargan datos de prueba y el usuario administrador.

---

## Estructura del proyecto

```text
JWT_auth_backend/
├── .vscode/
│   ├── launch.json
│   └── settings.json
│
├── app/
│   └── main.py
│
├── application/
│   └── services/
│       ├── auth_service.py
│       ├── curso_service.py
│       ├── estudiante_service.py
│       └── inscripcion_service.py
│
├── domain/
│   ├── curso.py
│   ├── errores_auth.py
│   ├── estudiante.py
│   ├── inscripcion.py
│   ├── refresh_token.py
│   └── usuario.py
│
├── infrastructure/
│   ├── database.py
│   │
│   ├── mappers/
│   │   ├── curso_mapper.py
│   │   ├── estudiante_mapper.py
│   │   ├── refresh_token_mapper.py
│   │   └── usuario_mapper.py
│   │
│   ├── models/
│   │   ├── curso_model.py
│   │   ├── estudiante_model.py
│   │   ├── inscripcion_model.py
│   │   ├── refresh_token_model.py
│   │   └── usuario_model.py
│   │
│   ├── repositories/
│   │   ├── curso_repository.py
│   │   ├── estudiante_repository.py
│   │   ├── inscripcion_repository.py
│   │   ├── refresh_token_repository.py
│   │   └── usuario_repository.py
│   │
│   ├── security/
│   │   ├── config.py
│   │   ├── jwt_service.py
│   │   ├── password_hasher.py
│   │   └── refresh_token_util.py
│   │
│   └── seeders/
│       ├── curso_seeder.py
│       ├── estudiante_seeder.py
│       ├── inscripcion_seeder.py
│       └── usuario_seeder.py
│
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_crear_tablas.py
│       ├── 0002_eliminar_tabla_alumnos.py
│       ├── 0003_crear_tabla_usuarios.py
│       └── 0004_crear_tabla_refresh_tokens.py
│
├── presentation/
│   ├── dependencies.py
│   │
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── curso_router.py
│   │   ├── estudiante_router.py
│   │   └── inscripcion_router.py
│   │
│   ├── schemas/
│   │   └── dtos/
│   │       ├── auth_dto.py
│   │       ├── curso_dto.py
│   │       ├── curso_query_dto.py
│   │       ├── estudiante_dto.py
│   │       └── estudiante_query_dto.py
│   │
│   └── security/
│       └── cookies.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Responsabilidad de cada capa

| Componente | Responsabilidad |
|---|---|
| `app/main.py` | Crea la aplicación FastAPI, configura CORS, carga los datos iniciales y registra los routers. |
| `presentation/routers` | Define los endpoints y recibe las solicitudes HTTP. |
| `presentation/schemas/dtos` | Contiene los DTO implementados con Pydantic. |
| `presentation/dependencies.py` | Abre una sesión por solicitud, construye los servicios con `Depends` y define `get_usuario_actual`, que valida el token. |
| `presentation/security/cookies.py` | Pone y borra la cookie del refresh token: las cookies son un detalle de HTTP. |
| `application/services` | Coordina los casos de uso. `AuthService` registra, inicia sesión, renueva y cierra sesiones. |
| `domain` | Entidades (`Estudiante`, `Curso`, `Inscripcion`, `Usuario`, `RefreshToken`), sus reglas y los errores de autenticación. |
| `infrastructure/database.py` | Lee el `.env`, crea el `engine` de PostgreSQL, la `SessionLocal` y la clase `Base`. |
| `infrastructure/models` | Modelos ORM: las tablas de la base de datos como clases de Python. |
| `infrastructure/mappers` | Convierten entre entidades de dominio y modelos ORM. |
| `infrastructure/repositories` | Guardan y recuperan datos usando una sesión de SQLAlchemy. |
| `infrastructure/security` | Detalles técnicos de seguridad: configuración, hash de contraseñas, JWT y refresh tokens. |
| `infrastructure/seeders` | Cargan datos iniciales para pruebas. |
| `migrations` | Migraciones de Alembic que crean y modifican el esquema. |

---

## Arquitectura

```text
CLIENTE
   │
   │ HTTP / JSON  (Authorization: Bearer <token>)
   ▼
┌─────────────────────────────────┐
│ PRESENTATION                    │
│                                 │
│ Routers + DTO / Pydantic        │
│ Depends → sesión por solicitud  │
│ get_usuario_actual → valida JWT │
│ cookies.py → cookie del refresh │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ APPLICATION                     │
│                                 │
│ AuthService                     │
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
│ Usuario, RefreshToken           │
│ Estado y comportamiento         │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ INFRASTRUCTURE                  │
│                                 │
│ Repositories → Mappers          │
│ Modelos ORM → Session           │
│ PasswordHasher, JwtService      │
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
Router + DTO Pydantic (+ get_usuario_actual en rutas protegidas)
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

El dominio y los servicios no conocen SQLAlchemy ni HTTP: trabajan con entidades de dominio. `AuthService` devuelve los tokens, pero no decide cómo viajan: eso lo resuelve la capa de presentación (el access token en el JSON y el refresh token en una cookie).

---

## Autenticación

### Tokens

| Token | Qué es | Dura | Dónde viaja | Dónde se guarda |
|---|---|---|---|---|
| **Access token** | JWT firmado con HS256 (`JWT_SECRET`). Claims: `sub`, `type`, `ver`, `iat`, `exp`, `jti`. | 15 minutos (`ACCESS_TOKEN_MINUTOS`) | Header `Authorization: Bearer <token>` | En ningún lado: la API lo valida con la firma. |
| **Refresh token** | Texto aleatorio de 43 caracteres (`secrets.token_urlsafe(32)`). | 7 días (`REFRESH_TOKEN_DIAS`) | Cookie `refresh_token` | En la tabla `refresh_tokens`, solo su hash SHA-256. |

### Flujo

```text
1. POST /auth/registro   → crea el usuario (no inicia sesión)
2. POST /auth/login      → { "access_token": "eyJ...", "token_type": "bearer" }
                           + cookie refresh_token
3. GET /estudiantes      → Authorization: Bearer eyJ...
4. (pasan 15 minutos)    → 401
5. POST /auth/refresh    → access token nuevo + refresh token nuevo en la cookie
6. POST /auth/logout     → revoca el refresh token y borra la cookie
```

### Endpoints de autenticación

| Método | Endpoint | Requiere token | Acción |
|---|---|---|---|
| `POST` | `/auth/registro` | No | Crea un usuario. Responde `201` con `id`, `email` y `activo`. |
| `POST` | `/auth/login` | No | Devuelve el access token y pone la cookie del refresh token. |
| `POST` | `/auth/refresh` | No (usa la cookie) | Rota el refresh token y devuelve un access token nuevo. |
| `POST` | `/auth/logout` | No (usa la cookie) | Revoca la sesión actual y borra la cookie. Responde `204` aunque no haya cookie. |
| `POST` | `/auth/logout-todos` | Sí | Cierra la sesión en todos los dispositivos. |
| `GET` | `/auth/me` | Sí | Devuelve el usuario dueño del token. |

### Medidas de seguridad

- **Contraseñas con Argon2id** (pwdlib): se guarda solo el hash, con salt propio por usuario.
- **Bloqueo por fuerza bruta:** 5 intentos fallidos bloquean la cuenta 15 minutos.
- **Mensajes genéricos:** email inexistente y contraseña incorrecta responden lo mismo (`401 "Credenciales inválidas."`), y el login con un email inexistente verifica contra un hash ficticio para tardar lo mismo.
- **Cookie del refresh token:** `HttpOnly` (JavaScript no la lee), `SameSite=strict` (no viaja desde otros sitios), `Path=/auth` (solo va a las rutas de autenticación) y `Secure` según `COOKIE_SECURE`.
- **Rotación y detección de reutilización:** cada refresh entrega un token nuevo y revoca el anterior. Si alguien reutiliza un refresh token ya usado, se revoca toda su familia (todas las sesiones que nacieron de ese login).
- **Logout global:** `logout-todos` incrementa `token_version` del usuario; los access tokens que tienen el `ver` anterior dejan de valer de inmediato.
- **Validación del JWT:** algoritmo fijo (`HS256`), claims obligatorios y `type == "access"`. Tokens con otro secreto o con `alg: none` responden `401`.
- **CORS:** solo acepta el origen `http://localhost:5173` (el frontend), con credenciales.

La contraseña mínima de registro es de **4 caracteres** para practicar cómodo en clase. En producción conviene 12 o más, como recomienda NIST.

### Usuario de prueba

Al iniciar la API, el seeder crea este usuario si no existe:

```text
email:      admin@academico.test
contraseña: clave-demo-solo-local
```

Es solo para desarrollo local.

### Probar con Swagger

1. Abre `http://localhost:8080/docs`.
2. Ejecuta `POST /auth/login` con el usuario de prueba y copia el valor de `access_token` (sin comillas).
3. Pulsa **Authorize** (el candado), pega el token **sin** escribir `Bearer` y pulsa **Authorize**.
4. Ejecuta `GET /estudiantes`: responde `200`. Con **Logout** en Authorize responde `401`.

El botón Authorize no valida el token: solo lo guarda y lo envía. La validación ocurre en la API al llamar a un endpoint protegido.

Para ver un token vencido sin esperar 15 minutos, pon `ACCESS_TOKEN_MINUTOS=1` en el `.env`, recrea el contenedor con `docker compose up -d`, espera un minuto y prueba `GET /estudiantes`.

### Desde un cliente (TypeScript)

La cookie del refresh token solo viaja si el cliente lo pide:

```typescript
const respuesta = await fetch("http://localhost:8080/auth/refresh", {
  method: "POST",
  credentials: "include",
});
```

El access token se guarda en memoria (no en `localStorage`) y se envía en cada request:

```typescript
fetch("http://localhost:8080/estudiantes", {
  headers: { Authorization: `Bearer ${accessToken}` },
});
```

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

┌───────────────────┐        ┌──────────────────┐
│ usuarios          │        │ refresh_tokens   │
├───────────────────┤        ├──────────────────┤
│ id (PK)           │1      n│ id (PK)          │
│ email (UQ)        ├────────┤ usuario_id (FK)  │
│ password_hash     │        │ token_hash (UQ)  │
│ activo            │        │ familia_id       │
│ token_version     │        │ expira_en        │
│ intentos_fallidos │        │ revocado_en      │
│ bloqueado_hasta   │        └──────────────────┘
└───────────────────┘
```

- `inscripciones` es la **tabla de asociación** de la relación muchos a muchos.
- Su clave primaria es el par (`estudiante_id`, `curso_id`): un estudiante no puede inscribirse dos veces en el mismo curso.
- Las claves foráneas usan `ON DELETE CASCADE`: al eliminar un estudiante o un curso, se eliminan sus inscripciones; al eliminar un usuario, se eliminan sus refresh tokens.
- `email` (en `estudiantes` y en `usuarios`), `codigo` y `token_hash` son únicos.
- `usuarios` y `estudiantes` son tablas independientes: un usuario es quien inicia sesión en la API.

En SQLAlchemy la relación muchos a muchos se declara con `relationship(secondary=...)`:

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

Todos los endpoints de esta sección **requieren** `Authorization: Bearer <access_token>`. Sin token, o con un token inválido o vencido, responden `401`. Los endpoints de autenticación están en la sección [Autenticación](#autenticación).

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

La protección se aplica por router, con una sola línea:

```python
router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"],
    dependencies=[Depends(get_usuario_actual)],
)
```

---

## Entidades de dominio

| Entidad | Atributos | Reglas |
|---|---|---|
| `Estudiante` | `id`, `nombre`, `apellido`, `email`, `activo` | Nombre, apellido y email obligatorios. Email único (sin distinguir mayúsculas). Propiedad `nombre_completo`. |
| `Curso` | `id`, `codigo`, `nombre`, `creditos`, `activo` | Código obligatorio, se guarda en mayúsculas y es único. Créditos ≥ 1. Propiedad `descripcion`. |
| `Inscripcion` | `estudiante_id`, `curso_id` | Une un estudiante con un curso. |
| `Usuario` | `id`, `email`, `password_hash`, `activo`, `token_version`, `intentos_fallidos`, `bloqueado_hasta` | Email obligatorio, en minúsculas. Guarda el hash, nunca la contraseña. Métodos `esta_bloqueado`, `registrar_fallo`, `registrar_exito` e `invalidar_sesiones`. |
| `RefreshToken` | `id`, `usuario_id`, `token_hash`, `familia_id`, `expira_en`, `revocado_en` | Método `esta_vigente`: no revocado y no vencido. |

Errores de autenticación (`domain/errores_auth.py`): `ErrorAutenticacion` y sus subclases `CredencialesInvalidas`, `CuentaBloqueada` y `TokenInvalido`. Los routers traducen cualquiera de ellas a `401`.

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
| `RegistroDTO` | Email y contraseña (`SecretStr`, entre 4 y 128 caracteres). |
| `LoginDTO` | Email y contraseña (mínimo 1 carácter). |
| `UsuarioResponseDTO` | `id`, `email` y `activo`: nunca expone el hash. |
| `TokenResponseDTO` | `access_token` y `token_type="bearer"`. |

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

`SecretStr` muestra `**********` en logs y errores; para leer la contraseña se usa `get_secret_value()`.

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

`RefreshTokenRepository.rotar` revoca el token actual y guarda el nuevo en **un solo commit** (una transacción): si algo falla en medio, no queda el usuario sin un token válido.

---

## Migraciones con Alembic

Las tablas **no** se crean al iniciar la API: se crean y modifican con migraciones. Alembic guarda en la tabla `alembic_version` qué migración está aplicada. `migrations/env.py` usa el mismo `engine` que la aplicación, así que también lee la conexión desde el `.env` (no hay credenciales en `alembic.ini`). Con Docker, el contenedor de la API ejecuta `alembic upgrade head` cada vez que arranca.

| Migración | Qué hace |
|---|---|
| `0001_crear_tablas.py` | Crea `estudiantes`, `cursos` e `inscripciones` con sus índices únicos y claves foráneas. |
| `0002_eliminar_tabla_alumnos.py` | Elimina la tabla antigua `alumnos`. |
| `0003_crear_tabla_usuarios.py` | Crea `usuarios`. |
| `0004_crear_tabla_refresh_tokens.py` | Crea `refresh_tokens`, con FK a `usuarios` y `ON DELETE CASCADE`. |

| Comando | Qué hace |
|---|---|
| `uv run alembic upgrade head` | Aplica todas las migraciones pendientes. |
| `uv run alembic downgrade -1` | Deshace la última migración. |
| `uv run alembic downgrade base` | Deshace todas las migraciones (borra las tablas). |
| `uv run alembic current` | Muestra la migración aplicada. |
| `uv run alembic history` | Lista todas las migraciones. |
| `uv run alembic revision --autogenerate --rev-id 0005 -m "mensaje"` | Crea una migración comparando los modelos con la base de datos. `--rev-id` mantiene la numeración. |
| `uv run alembic check` | Indica si hay cambios en los modelos sin migración. |

Para correr Alembic desde tu PC contra la base de datos de Docker, el contenedor `db` debe estar encendido (`docker compose up -d db`) y el `.env` debe tener `DB_HOST=localhost` y `DB_PORT=5433`.

Flujo para cambiar un modelo (por ejemplo, agregar una columna):

```text
1. Modificar el modelo en infrastructure/models/
2. Si es un modelo nuevo, importarlo en migrations/env.py
3. uv run alembic revision --autogenerate --rev-id 0005 -m "agregar columna telefono"
4. Revisar el archivo generado en migrations/versions/
5. uv run alembic upgrade head   (o docker compose up -d --build)
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

Aparte, `cargar_usuarios_iniciales()` crea el usuario `admin@academico.test` si todavía no existe, aunque la base ya tenga estudiantes. El seeder de usuarios pasa siempre por `AuthService.registrar`, así la contraseña queda hasheada.

Si la base de datos ya tiene datos, los seeders no se ejecutan.

---

## Recorrido de una solicitud protegida

```http
POST /estudiantes/1/cursos/5
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

```text
Cliente
   │ POST /estudiantes/1/cursos/5  + Authorization: Bearer ...
   ▼
FastAPI
   │ valida los parámetros de ruta (> 0)
   │ get_session() abre una sesión
   │ get_usuario_actual()
   │    verifica la firma, exp y type del JWT
   │    carga el usuario y compara token_version   → si falla, 401
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

Abre `http://localhost:8080/docs`, autentícate como se explica en [Probar con Swagger](#probar-con-swagger) y prueba:

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
| `201 Created` | Recurso creado, usuario registrado o inscripción realizada |
| `204 No Content` | Recurso eliminado, estudiante retirado del curso o sesión cerrada |
| `400 Bad Request` | Regla de aplicación inválida (email o código duplicado, inscripción repetida, entidad inactiva) |
| `401 Unauthorized` | Falta el token o es inválido o vencido, credenciales incorrectas, cuenta bloqueada o refresh token inválido |
| `404 Not Found` | Estudiante, curso o inscripción inexistente |
| `422 Unprocessable Entity` | Error de validación (por ejemplo, contraseña de menos de 4 caracteres) |

---

## Depuración con VS Code

El proyecto incluye `.vscode/launch.json`. Para iniciar la depuración:

```text
Ctrl + Shift + D → "Depurar API de estudiantes" → F5
```

La configuración levanta la API en tu PC (no en Docker) en el puerto `8001`. Necesita el `.env` con la base de datos accesible: por ejemplo, `docker compose up -d db` y `DB_PORT=5433`. Si ese puerto está ocupado, cambia el valor en `.vscode/launch.json`.

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

### Falta JWT_SECRET en el archivo .env

Docker Compose no encuentra el secreto. Genera uno con `python -c "import secrets; print(secrets.token_urlsafe(64))"` y agrégalo al `.env` como `JWT_SECRET=...`. Sin Docker, el mismo problema aparece como `KeyError: 'JWT_SECRET'`.

### KeyError: 'DB_USER' (u otra variable `DB_*`)

Falta el archivo `.env` o le falta esa variable. Copia `.env.example` como `.env` y completa los datos.

### no configuration file provided: not found

Ejecutaste `docker compose` fuera de la carpeta del proyecto. Entra primero a la carpeta que tiene `docker-compose.yml`.

### Connection refused al ejecutar Alembic desde tu PC

- El contenedor de la base de datos está apagado: `docker compose up -d db`.
- El puerto no coincide: la base de Docker está en el **5433**, no en el 5432. Revisa `DB_PORT` en el `.env`.

### relation "usuarios" does not exist (o cualquier otra tabla)

Las migraciones no están aplicadas. Con Docker, reconstruye la imagen para que incluya las migraciones nuevas:

```bash
docker compose up -d --build
```

Sin Docker:

```bash
uv run alembic upgrade head
```

### 401 en Swagger aunque pegué el token

- Pegaste `Bearer eyJ...`: Swagger agrega `Bearer` solo, pega únicamente el token.
- Pegaste el token con comillas.
- Pasaron más de 15 minutos desde el login: inicia sesión otra vez o usa `POST /auth/refresh`.
- Llamaste a `logout-todos`: los tokens anteriores dejan de valer.
- Fallaste 5 veces la contraseña: la cuenta queda bloqueada 15 minutos.

### El registro no devuelve un token

Es lo esperado: `POST /auth/registro` solo crea el usuario. El token se obtiene con `POST /auth/login`.

### DuplicateTable al ejecutar `alembic upgrade head`

Las tablas ya existían antes de usar Alembic (por ejemplo, creadas con `create_all`). Marca la base de datos como actualizada sin volver a crearlas:

```bash
uv run alembic stamp head
```

### Address already in use

El puerto ya está siendo utilizado. Inicia Uvicorn en otro puerto, o cambia `APP_PORT` en el `.env` si usas Docker:

```bash
uv run uvicorn app.main:app --reload --port 8765
```

### No module named 'app'

Ejecuta los comandos desde la raíz del proyecto (la carpeta que tiene `pyproject.toml`).

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
- Docker y Docker Compose.
- Autenticación: hash de contraseñas, JWT, refresh tokens con rotación, cookies seguras, logout y CORS.

Todavía no se incorporan:

- Pruebas automatizadas.
- Autorización por roles (por ejemplo, que solo un administrador pueda eliminar).
- Verificación de email y recuperación de contraseña.
- CI/CD.

El proyecto continuará evolucionando progresivamente durante el curso.
