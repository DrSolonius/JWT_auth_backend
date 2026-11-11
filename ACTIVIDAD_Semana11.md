# Actividad práctica — Testing en Backend (Semana 11)

**Modalidad:** grupal · **Proyecto base:** este repositorio (`backend_S11_testing`)

## Contexto

El Sistema Académico (FastAPI + SQLAlchemy + PostgreSQL + JWT) ya tiene una suite de 59 tests en `tests/unit`, `tests/integration` y `tests/api`.
Tu grupo la va a **ampliar** y va a incorporar una **regla de negocio nueva escribiendo primero el test** (TDD).

> **Regla nueva:** el email de un estudiante debe contener el carácter `@`.
> En caso contrario se rechaza con el mensaje `El email debe contener @.`

Todos los tests nuevos van en `tests/actividad/`, separados por nivel:

```text
tests/actividad/
  unit/
  integration/
  api/
```

Cada carpeta necesita su `__init__.py`. Los fixtures `session`, `repository`, `service` y `client` de `tests/conftest.py` están disponibles en los tres niveles (`client` ya viene autenticado).

## Preparación

```bash
uv sync --group dev
uv run pytest
```

Debes ver `59 passed` antes de empezar. No necesitas `.env` ni Docker: los tests usan una base SQLite en memoria (ver `tests/conftest.py`).

## Parte 1 — Tests unitarios (rojo)

Archivo: `tests/actividad/unit/test_estudiante_email.py`

1. Un email sin `@` es rechazado por `Estudiante` (usa `@pytest.mark.parametrize` con al menos 3 valores).
2. Un email con `@` es aceptado.
3. Un email vacío sigue fallando con `El email es obligatorio.`

Ejecuta `uv run pytest tests/actividad/unit` y **verifica que el caso 1 falla**: todavía no existe la regla.

## Parte 2 — Implementar la regla (verde)

En `domain/estudiante.py`, dentro de `__post_init__`, agrega la validación y ejecuta de nuevo los tests unitarios hasta que pasen.

## Parte 3 — Tests de integración

Archivo: `tests/actividad/integration/test_servicio_actividad.py`

1. `service.obtener` de un id inexistente retorna `None`.
2. `service.listar` sin estudiantes retorna `([], 0)`.
3. `service.listar` con una página fuera de rango retorna una lista vacía y el total correcto.
4. Eliminar un estudiante **elimina también sus inscripciones** (usa `CursoRepository` e `InscripcionRepository` con el fixture `session`).
5. `service.crear` con un email sin `@` lanza `ValueError`.

## Parte 4 — Tests de API

Archivo: `tests/actividad/api/test_api_actividad.py`

1. `PUT /estudiantes/{id}` con el email de **otro** estudiante responde `400`.
2. `POST /estudiantes` con un email sin `@` responde `400` con el detalle del error.
3. `GET /estudiantes?pagina=5&tamano=10` responde `200` con `items` vacío.

## Parte 5 — Cobertura

```bash
uv run pytest --cov --cov-report=term-missing
```

La cobertura se mide solo sobre el módulo de estudiantes (ver `[tool.coverage.run]` en `pyproject.toml`).
El proyecto parte con **98 %**. Usa la columna `Missing` para encontrar qué líneas nunca se ejecutan y escribe los tests que faltan hasta llegar al **100 %**.

> Pista: hay una línea en el repositorio y dos en el router que no se alcanzan con los tests actuales. ¿Qué petición o llamada las ejecutaría?

## Entregable

1. El proyecto con los tests nuevos en `tests/actividad/` y la regla implementada.
2. Captura de pantalla de `uv run pytest` con todos los tests en verde.
3. Captura del reporte de cobertura.
4. Respuestas breves (máx. 5 líneas cada una):
   - ¿Qué valida un test unitario, uno de integración y uno de API? Da un ejemplo de esta actividad.
   - ¿Por qué cada test recibe una `session` (base SQLite en memoria) nueva en lugar de compartir una?
   - ¿Qué ventaja y qué riesgo tiene probar con SQLite si la aplicación usa PostgreSQL?
   - ¿Qué mide la cobertura y qué no mide?

## Criterio de logro

La actividad se considera lograda si todos los tests pasan, la regla nueva está cubierta en los tres niveles y el grupo puede explicar qué valida cada nivel.
