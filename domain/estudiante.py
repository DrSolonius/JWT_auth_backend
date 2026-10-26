from dataclasses import dataclass


@dataclass
class Estudiante:
    nombre: str
    apellido: str
    email: str
    id: int | None = None
    activo: bool = True

    def __post_init__(self) -> None:
        self.nombre = self.nombre.strip()
        self.apellido = self.apellido.strip()
        self.email = self.email.strip()

        if not self.nombre:
            raise ValueError("El nombre es obligatorio.")

        if not self.apellido:
            raise ValueError("El apellido es obligatorio.")

        if not self.email:
            raise ValueError("El email es obligatorio.")

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def desactivar(self) -> None:
        self.activo = False

    def activar(self) -> None:
        self.activo = True