"""Tests unitarios de la regla de paginación del servicio.

Usamos un repositorio FALSO (fake): el servicio se prueba aislado,
sin depender del repositorio real.
"""
import pytest

from application.services.estudiante_service import EstudianteService


class RepositorioFalso:
    """Registra con qué parámetros lo llamó el servicio."""

    def __init__(self) -> None:
        self.llamadas: list[tuple[int, int]] = []

    def listar(self, offset: int, limite: int) -> list:
        self.llamadas.append((offset, limite))
        return []

    def contar(self) -> int:
        return 0


@pytest.fixture
def repo_falso() -> RepositorioFalso:
    return RepositorioFalso()


@pytest.fixture
def service(repo_falso) -> EstudianteService:
    return EstudianteService(repo_falso, None)


# Boundary Value Analysis: probamos EN el borde y a ambos lados.
@pytest.mark.parametrize("tamano", [1, 2, 99, 100])
def test_tamano_valido_es_aceptado(service, tamano):
    service.listar(pagina=1, tamano=tamano)


@pytest.mark.parametrize("tamano", [-1, 0, 101])
def test_tamano_fuera_de_rango_es_rechazado(service, tamano):
    with pytest.raises(ValueError, match="entre 1 y 100"):
        service.listar(pagina=1, tamano=tamano)


def test_pagina_1_es_valida(service):
    service.listar(pagina=1, tamano=10)


@pytest.mark.parametrize("pagina", [0, -1])
def test_pagina_menor_a_1_es_rechazada(service, pagina):
    with pytest.raises(ValueError, match="mayor o igual a 1"):
        service.listar(pagina=pagina, tamano=10)


@pytest.mark.parametrize(
    "pagina, tamano, offset_esperado",
    [(1, 10, 0), (2, 10, 10), (3, 25, 50)],
)
def test_el_servicio_calcula_el_offset(
    service, repo_falso, pagina, tamano, offset_esperado
):
    service.listar(pagina=pagina, tamano=tamano)

    assert repo_falso.llamadas == [(offset_esperado, tamano)]
