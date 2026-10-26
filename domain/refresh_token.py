from dataclasses import dataclass
from datetime import datetime


@dataclass
class RefreshToken:
    usuario_id: int
    token_hash: str
    familia_id: str
    expira_en: datetime
    id: int | None = None
    revocado_en: datetime | None = None

    def esta_vigente(self, ahora: datetime) -> bool:
        return self.revocado_en is None and self.expira_en > ahora
