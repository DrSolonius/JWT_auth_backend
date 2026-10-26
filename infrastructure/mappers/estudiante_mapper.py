from domain.estudiante import Estudiante
from infrastructure.models.estudiante_model import EstudianteModel


def a_dominio(modelo: EstudianteModel) -> Estudiante:
    return Estudiante(
        id=modelo.id,
        nombre=modelo.nombre,
        apellido=modelo.apellido,
        email=modelo.email,
        activo=modelo.activo,
    )


def a_modelo(estudiante: Estudiante) -> EstudianteModel:
    return EstudianteModel(
        id=estudiante.id,
        nombre=estudiante.nombre,
        apellido=estudiante.apellido,
        email=estudiante.email,
        activo=estudiante.activo,
    )


def actualizar_modelo(modelo: EstudianteModel, estudiante: Estudiante) -> None:
    modelo.nombre = estudiante.nombre
    modelo.apellido = estudiante.apellido
    modelo.email = estudiante.email
    modelo.activo = estudiante.activo
