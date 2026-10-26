from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.curso import Curso
from infrastructure.mappers import curso_mapper
from infrastructure.models.curso_model import CursoModel


class CursoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, curso: Curso) -> Curso:
        modelo = curso_mapper.a_modelo(curso)

        self.session.add(modelo)
        self.session.commit()
        self.session.refresh(modelo)

        return curso_mapper.a_dominio(modelo)

    def obtener_por_id(self, curso_id: int) -> Curso | None:
        modelo = self.session.get(CursoModel, curso_id)

        if modelo is None:
            return None

        return curso_mapper.a_dominio(modelo)

    def obtener_por_codigo(self, codigo: str) -> Curso | None:
        codigo_buscado = codigo.strip().upper()

        modelo = self.session.scalars(
            select(CursoModel).where(CursoModel.codigo == codigo_buscado)
        ).first()

        if modelo is None:
            return None

        return curso_mapper.a_dominio(modelo)

    def listar(self, offset: int, limite: int) -> list[Curso]:
        modelos = self.session.scalars(
            select(CursoModel)
            .order_by(CursoModel.id)
            .offset(offset)
            .limit(limite)
        ).all()

        return [curso_mapper.a_dominio(modelo) for modelo in modelos]

    def contar(self) -> int:
        return self.session.scalar(
            select(func.count()).select_from(CursoModel)
        )

    def actualizar(self, curso: Curso) -> Curso:
        modelo = self.session.get(CursoModel, curso.id)

        if modelo is None:
            raise ValueError("El curso no existe.")

        curso_mapper.actualizar_modelo(modelo, curso)
        self.session.commit()
        self.session.refresh(modelo)

        return curso_mapper.a_dominio(modelo)

    def eliminar(self, curso_id: int) -> bool:
        modelo = self.session.get(CursoModel, curso_id)

        if modelo is None:
            return False

        self.session.delete(modelo)
        self.session.commit()
        return True
