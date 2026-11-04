from application.services.auth_service import AuthService


def seed_admin(service: AuthService, email: str, password: str) -> None:
    # Siempre a través del servicio: así la contraseña queda hasheada.
    service.asegurar_admin(email, password)
