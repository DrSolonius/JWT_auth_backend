# Actividad — Semana 12: Integración Continua con GitHub Actions

**Objetivo:** dejar un pipeline que ejecute los 59 tests en cada pull request, con PostgreSQL real, y una regla que impida fusionar a `main` si falla.

**Tiempo estimado:** 60 a 75 minutos.

## Antes de empezar

Necesitas: cuenta de GitHub, Git, Docker Desktop, `uv` y Python 3.14 (lo instala `uv`).

Todo el trabajo se hace en **tu propio repositorio**, creado a partir de la plantilla del curso. Las reglas de rama y los secrets se crean en un repositorio que sea tuyo.

## Preparación

1. En GitHub, abre `DrSolonius/CD_CI_sistema_academico` y pulsa **Use this template**, luego **Create a new repository**. Ponle el nombre que quieras, déjalo **Public** y créalo en tu cuenta.
2. Clona **tu repositorio** (cambia `TU_USUARIO` y, si lo cambiaste, el nombre):

```bash
git clone https://github.com/TU_USUARIO/CD_CI_sistema_academico.git
cd CD_CI_sistema_academico
```

3. Comprueba que los tests pasan en tu computador:

```bash
cp .env.example .env             # completa TEST_DB_PASSWORD y las demás claves
docker compose up -d db          # PostgreSQL; crea también la base clase_test
uv sync --group dev
uv run pytest
```

Debes ver `59 passed`. Si ves `Faltan variables para la base de pruebas`, falta completar las líneas `TEST_DB_*` de tu `.env`.

> El repositorio no trae ningún workflow: la carpeta `.github/workflows/` no existe, y la creas tú en la Parte 1.

---

## Parte 1 — Un workflow mínimo (rojo esperado)

Crea una rama de trabajo y, dentro, la carpeta y el archivo `.github/workflows/ci.yml`:

```bash
git switch -c mi-ci
```

Contenido de `ci.yml`:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: astral-sh/setup-uv@v10.3.3

      - run: uv sync --group dev

      - run: uv run pytest
```

Súbelo y abre un pull request de `mi-ci` hacia `main` en tu repositorio:

```bash
git add .github/workflows/ci.yml
git commit -m "ci: workflow mínimo"
git push -u origin mi-ci
```

> Abre el PR desde el enlace que muestra `git push`, o desde la pestaña *Pull requests*. Comprueba que *base* sea `main` de **tu** repositorio.

**Qué debes observar:** el check `tests` termina en **rojo**. Abre el paso `Run uv run pytest` y lee el mensaje: `Faltan variables para la base de pruebas`.

**Pregunta 1:** ¿por qué falla si en tu computador pasan los 59 tests?

## Parte 2 — PostgreSQL como service y un secret (verde)

1. **Crea el secret.** En tu repositorio: *Settings, Secrets and variables, Actions, New repository secret*. Nombre: `TEST_DB_PASSWORD`. Valor: la contraseña que quieras (la base de CI es desechable). El nombre debe ser exactamente ese.
2. Agrega al job `tests` el bloque `services` y las variables `env`. El resultado completo del job es:

```yaml
# .github/workflows/ci.yml
jobs:
  tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: alumno
          POSTGRES_PASSWORD: ${{ secrets.TEST_DB_PASSWORD }}
          POSTGRES_DB: clase_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U alumno -d clase_test"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10

    env:
      TEST_DB_HOST: localhost
      TEST_DB_PORT: 5432
      TEST_DB_NAME: clase_test
      TEST_DB_USER: alumno
      TEST_DB_PASSWORD: ${{ secrets.TEST_DB_PASSWORD }}

    steps:
      # ... los mismos pasos de la Parte 1
```

3. Haz commit y push: el PR se vuelve a ejecutar solo.

**Qué debes observar:** el check `tests` en **verde** y `59 passed` en el log.

**Pregunta 2:** ¿para qué sirve el `--health-cmd`? ¿Qué pasaría sin él?

## Parte 3 — Cobertura como compuerta

Cambia el último paso por:

```yaml
      - run: uv run pytest --cov
```

**Qué debes observar:** en el log aparece la tabla de cobertura y la línea `Required test coverage of 85.0% reached`. El umbral está en `pyproject.toml` (`fail_under = 85`).

**Pregunta 3:** ¿qué pasaría si borras tests y la cobertura baja de 85 %? Compruébalo en tu computador con `uv run pytest --cov`.

## Parte 4 — Proteger `main`

En tu repositorio: *Settings, Branches, Add branch protection rule* (o *Add classic branch protection rule*), con la rama `main`:

- Activa **Require a pull request before merging**.
- Activa **Require status checks to pass before merging**, y en el buscador elige **`tests`**.

> El check aparece en la lista solo si ya se ejecutó al menos una vez. Si no lo ves, espera a que termine la ejecución de la Parte 2.
> La regla exige el job por su nombre: si lo renombras en el YAML, deja de aplicar.
> Las reglas de rama están disponibles en repositorios públicos con cuenta gratuita.

**Qué debes observar:** en tu PR con el check verde, el botón de merge está habilitado.

## Parte 5 — Caché y medición

1. Anota el tiempo total de la última ejecución (pestaña Actions, la duración aparece junto a la ejecución).
2. Activa el caché en el paso de `setup-uv`:

```yaml
      - uses: astral-sh/setup-uv@v10.3.3
        with:
          enable-cache: true
```

3. Haz push (primera ejecución con caché: crea el caché) y luego **vuelve a ejecutar** el workflow con *Re-run all jobs* (segunda ejecución: lo usa).
4. Anota el tiempo de la segunda ejecución.

**Qué debes observar:** el paso de instalación de dependencias baja de tiempo en la segunda ejecución.

**Pregunta 4:** ¿cuánto ahorró el caché? ¿Qué cambio haría que el caché se descarte? (Pista: `uv.lock`.)

## Parte 6 — Romper un test a propósito

1. Crea una rama y cambia un `assert` para que falle. Por ejemplo, en `tests/unit/test_estudiante.py`, un valor esperado distinto del real.
2. Haz commit, push y abre un PR hacia `main` de tu repositorio.

```bash
git switch -c romper-test
# edita el test
git add -A
git commit -m "prueba: test roto a propósito"
git push -u origin romper-test
```

**Qué debes observar:** el check `tests` en **rojo**, el log indica qué test falló y **el botón de merge está bloqueado**.

3. Corrige el test y haz push. El check vuelve a verde y el merge se habilita.

**Pregunta 5:** ¿qué habría pasado sin la regla de la Parte 4? ¿Y sin el pipeline?

---

## Entregable

1. Enlace al pull request de la Parte 2 con el check `tests` en verde.
2. Captura del pull request de la Parte 6 con el check en rojo y el merge bloqueado.
3. Los dos tiempos de la Parte 5 (sin caché y con caché).
4. Respuestas breves (máx. 5 líneas cada una) a las preguntas 1 a 5.

## Criterio de logro

- El workflow ejecuta los 59 tests con PostgreSQL y termina en verde.
- La contraseña de la base no aparece escrita en ningún archivo del repositorio.
- `main` no se puede fusionar con el check en rojo.

## Errores frecuentes

| Síntoma | Causa probable |
|---|---|
| No aparece ninguna ejecución | El archivo no está en `.github/workflows/` (con esa ruta exacta) o no se subió con `git push`; revisa también la pestaña Actions. |
| El PR no muestra ningún check | El workflow solo corre en pull requests y en push a `main`; comprueba que el PR sea hacia `main`. |
| `Faltan variables para la base de pruebas` | Faltan las `TEST_DB_*` en el bloque `env` del job, o el secret no existe. |
| El job se queda esperando o falla al arrancar PostgreSQL | El secret `TEST_DB_PASSWORD` no existe o está mal escrito: la base no arranca sin contraseña. |
| Error de YAML al subir | Indentación: el YAML usa 2 espacios y no acepta tabulaciones. |
| El check `tests` no aparece al crear la regla | El workflow todavía no se ejecutó, o el job tiene otro nombre. |
| `connection refused` en los tests | El puerto del `service` no coincide con `TEST_DB_PORT` (ambos 5432). |
