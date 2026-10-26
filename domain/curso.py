from dataclasses import dataclass


@dataclass
class Curso:
    codigo: str
    nombre: str
    creditos: int
    id: int | None = None
    activo: bool = True

    def __post_init__(self) -> None:
        self.codigo = self.codigo.strip().upper()
        self.nombre = self.nombre.strip()

        if not self.codigo:
            raise ValueError("El código es obligatorio.")

        if not self.nombre:
            raise ValueError("El nombre es obligatorio.")

        if self.creditos < 1:
            raise ValueError("Los créditos deben ser mayores o iguales a 1.")

    @property
    def descripcion(self) -> str:
        return f"{self.codigo} - {self.nombre}"

    def desactivar(self) -> None:
        self.activo = False

    def activar(self) -> None:
        self.activo = True
