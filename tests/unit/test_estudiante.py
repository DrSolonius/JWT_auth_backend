"""Tests unitarios de la entidad de dominio Estudiante.

No hay servicio, repositorio ni HTTP: solo la regla de negocio.
"""
import pytest

from domain.estudiante import Estudiante


def crear_estudiante(**cambios) -> Estudiante:
    datos = {"nombre": "Ana", "apellido": "Pérez", "email": "ana@example.com"}
    datos.update(cambios)
    return Estudiante(**datos)


def test_estudiante_nuevo_queda_activo_y_sin_id():
    estudiante = crear_estudiante()

    assert estudiante.activo is True
    assert estudiante.id is None


def test_nombre_completo_une_nombre_y_apellido():
    estudiante = crear_estudiante(nombre="Ana", apellido="Pérez")

    assert estudiante.nombre_completo == "Ana Pérez"


def test_espacios_alrededor_se_eliminan():
    estudiante = crear_estudiante(nombre="  Ana ", email=" ana@example.com  ")

    assert estudiante.nombre == "Ana"
    assert estudiante.email == "ana@example.com"


@pytest.mark.parametrize(
    "campo, mensaje",
    [
        ("nombre", "El nombre es obligatorio."),
        ("apellido", "El apellido es obligatorio."),
        ("email", "El email es obligatorio."),
    ],
)
@pytest.mark.parametrize("valor_invalido", ["", "   "])
def test_campos_obligatorios_vacios_son_rechazados(
    campo, mensaje, valor_invalido
):
    with pytest.raises(ValueError, match=mensaje):
        crear_estudiante(**{campo: valor_invalido})


def test_desactivar_y_activar_cambian_el_estado():
    estudiante = crear_estudiante()

    estudiante.desactivar()
    assert estudiante.activo is False

    estudiante.activar()
    assert estudiante.activo is True
