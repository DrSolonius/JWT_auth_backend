from dataclasses import dataclass
from datetime import datetime, timedelta


MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 15


@dataclass
class Usuario:
    email: str
    password_hash: str
    id: int | None = None
    activo: bool = True
    token_version: int = 0
    intentos_fallidos: int = 0
    bloqueado_hasta: datetime | None = None

    def __post_init__(self) -> None:
        self.email = self.email.strip().lower()

        if not self.email:
            raise ValueError("El email es obligatorio.")

    def invalidar_sesiones(self) -> None:
        self.token_version += 1

    def esta_bloqueado(self, ahora: datetime) -> bool:
        return self.bloqueado_hasta is not None and self.bloqueado_hasta > ahora

    def registrar_fallo(self, ahora: datetime) -> None:
        self.intentos_fallidos += 1

        if self.intentos_fallidos >= MAX_INTENTOS:
            self.bloqueado_hasta = ahora + timedelta(minutes=MINUTOS_BLOQUEO)
            self.intentos_fallidos = 0

    def registrar_exito(self) -> None:
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
