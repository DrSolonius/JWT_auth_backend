from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.estudiante import Estudiante
from infrastructure.mappers import estudiante_mapper
from infrastructure.models.estudiante_model import EstudianteModel


class EstudianteRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, estudiante: Estudiante) -> Estudiante:
        modelo = estudiante_mapper.a_modelo(estudiante)

        self.session.add(modelo)
        self.session.commit()
        self.session.refresh(modelo)

        return estudiante_mapper.a_dominio(modelo)

    def obtener_por_id(self, estudiante_id: int) -> Estudiante | None:
        modelo = self.session.get(EstudianteModel, estudiante_id)

        if modelo is None:
            return None

        return estudiante_mapper.a_dominio(modelo)

    def obtener_por_email(self, email: str) -> Estudiante | None:
        email_buscado = email.strip().lower()

        modelo = self.session.scalars(
            select(EstudianteModel).where(
                func.lower(EstudianteModel.email) == email_buscado
            )
        ).first()

        if modelo is None:
            return None

        return estudiante_mapper.a_dominio(modelo)

    def listar(self, offset: int, limite: int) -> list[Estudiante]:
        modelos = self.session.scalars(
            select(EstudianteModel)
            .order_by(EstudianteModel.id)
            .offset(offset)
            .limit(limite)
        ).all()

        return [estudiante_mapper.a_dominio(modelo) for modelo in modelos]

    def contar(self) -> int:
        return self.session.scalar(
            select(func.count()).select_from(EstudianteModel)
        )

    def actualizar(self, estudiante: Estudiante) -> Estudiante:
        modelo = self.session.get(EstudianteModel, estudiante.id)

        if modelo is None:
            raise ValueError("El estudiante no existe.")

        estudiante_mapper.actualizar_modelo(modelo, estudiante)
        self.session.commit()
        self.session.refresh(modelo)

        return estudiante_mapper.a_dominio(modelo)

    def eliminar(self, estudiante_id: int) -> bool:
        modelo = self.session.get(EstudianteModel, estudiante_id)

        if modelo is None:
            return False

        self.session.delete(modelo)
        self.session.commit()
        return True
