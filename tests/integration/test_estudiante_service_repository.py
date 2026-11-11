"""Tests de integración: EstudianteService + EstudianteRepository REALES.

Aquí no hay falsos: verificamos que las dos piezas colaboren bien.
"""
import pytest


def test_crear_asigna_id_y_deja_el_estudiante_guardado(service):
    creado = service.crear("Ana", "Pérez", "ana@example.com")

    assert creado.id == 1
    assert service.obtener(creado.id).email == "ana@example.com"


def test_ids_son_correlativos(service):
    primero = service.crear("Ana", "Pérez", "ana@example.com")
    segundo = service.crear("Luis", "Muñoz", "luis@example.com")

    assert (primero.id, segundo.id) == (1, 2)


def test_email_duplicado_es_rechazado(service):
    service.crear("Ana", "Pérez", "ana@example.com")

    with pytest.raises(ValueError, match="Ya existe un estudiante"):
        service.crear("Otra", "Persona", "ana@example.com")


def test_email_duplicado_ignora_mayusculas(service):
    service.crear("Ana", "Pérez", "ana@example.com")

    with pytest.raises(ValueError, match="Ya existe un estudiante"):
        service.crear("Otra", "Persona", "ANA@EXAMPLE.COM")


def test_actualizar_puede_conservar_el_propio_email(service):
    creado = service.crear("Ana", "Pérez", "ana@example.com")

    actualizado = service.actualizar(
        creado.id, "Ana María", "Pérez", "ana@example.com"
    )

    assert actualizado.nombre == "Ana María"


def test_actualizar_no_puede_usar_el_email_de_otro(service):
    service.crear("Ana", "Pérez", "ana@example.com")
    luis = service.crear("Luis", "Muñoz", "luis@example.com")

    with pytest.raises(ValueError, match="Ya existe un estudiante"):
        service.actualizar(luis.id, "Luis", "Muñoz", "ana@example.com")


def test_actualizar_inexistente_retorna_none(service):
    assert service.actualizar(99, "A", "B", "a@b.cl") is None


def test_eliminar_quita_al_estudiante(service):
    creado = service.crear("Ana", "Pérez", "ana@example.com")

    assert service.eliminar(creado.id) is True
    assert service.obtener(creado.id) is None


def test_eliminar_inexistente_retorna_false(service):
    assert service.eliminar(99) is False


def test_listar_pagina_los_resultados_reales(service):
    for i in range(1, 26):
        service.crear(f"N{i}", f"A{i}", f"e{i}@example.com")

    pagina3, total = service.listar(pagina=3, tamano=10)

    assert total == 25
    assert [e.id for e in pagina3] == [21, 22, 23, 24, 25]


def test_los_tests_no_comparten_datos(service):
    """Gracias al fixture, el repositorio de este test parte vacío."""
    _, total = service.listar(pagina=1, tamano=10)

    assert total == 0
