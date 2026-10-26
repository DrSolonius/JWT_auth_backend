from pwdlib import PasswordHash


class PasswordHasher:
    def __init__(self) -> None:
        self._hash = PasswordHash.recommended()  # Argon2id
        # Se usa en el login cuando el email no existe, para igualar los tiempos.
        self.hash_ficticio = self.hashear("clave-ficticia")

    def hashear(self, password: str) -> str:
        return self._hash.hash(password)

    def verificar(self, password: str, password_hash: str) -> bool:
        return self._hash.verify(password, password_hash)

    def verificar_y_actualizar(self, password: str, password_hash: str):
        """Devuelve (ok, hash_nuevo | None) si cambian los parámetros."""
        return self._hash.verify_and_update(password, password_hash)
