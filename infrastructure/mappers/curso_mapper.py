from domain.curso import Curso
from infrastructure.models.curso_model import CursoModel


def a_dominio(modelo: CursoModel) -> Curso:
    return Curso(
        id=modelo.id,
        codigo=modelo.codigo,
        nombre=modelo.nombre,
        creditos=modelo.creditos,
        activo=modelo.activo,
    )


def a_modelo(curso: Curso) -> CursoModel:
    return CursoModel(
        id=curso.id,
        codigo=curso.codigo,
        nombre=curso.nombre,
        creditos=curso.creditos,
        activo=curso.activo,
    )


def actualizar_modelo(modelo: CursoModel, curso: Curso) -> None:
    modelo.codigo = curso.codigo
    modelo.nombre = curso.nombre
    modelo.creditos = curso.creditos
    modelo.activo = curso.activo
