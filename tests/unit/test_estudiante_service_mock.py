"""Tests unitarios del servicio con MOCKS (unittest.mock).

A diferencia del fake, un Mock registra cómo lo llamaron: así podemos
verificar que el servicio usó bien sus dependencias.
"""
from unittest.mock import Mock

import pytest

from application.services.estudiante_service import EstudianteService
from domain.estudiante import Estudiante


@pytest.fixture
def repo() -> Mock:
    return Mock()


@pytest.fixture
def inscripciones() -> Mock:
    return Mock()


@pytest.fixture
def service(repo, inscripciones) -> EstudianteService:
    return EstudianteService(repo, inscripciones)


def test_listar_pide_offset_y_limite_correctos(service, repo):
    repo.listar.return_value = []
    repo.contar.return_value = 0

    service.listar(pagina=3, tamano=10)

    repo.listar.assert_called_once_with(offset=20, limite=10)


def test_crear_con_email_duplicado_no_guarda(service, repo):
    repo.obtener_por_email.return_value = Estudiante(
        nombre="Ana", apellido="Pérez", email="ana@example.com", id=1
    )

    with pytest.raises(ValueError, match="Ya existe"):
        service.crear("Otra", "Persona", "ana@example.com")

    repo.crear.assert_not_called()


@pytest.mark.parametrize("eliminado, se_limpia", [(True, True), (False, False)])
def test_eliminar_limpia_inscripciones_solo_si_elimino(
    service, repo, inscripciones, eliminado, se_limpia
):
    repo.eliminar.return_value = eliminado

    service.eliminar(7)

    assert inscripciones.eliminar_por_estudiante.called is se_limpia
    if se_limpia:
        inscripciones.eliminar_por_estudiante.assert_called_once_with(7)


def test_error_del_repositorio_se_propaga(service, repo):
    repo.listar.side_effect = RuntimeError("base caída")

    with pytest.raises(RuntimeError, match="base caída"):
        service.listar(pagina=1, tamano=10)
