from application.services.auth_service import AuthService


EMAIL_ADMIN = "admin@academico.test"


def seed_usuarios(service: AuthService) -> None:
    # Siempre a través del servicio: así la contraseña queda hasheada.
    service.registrar(
        email=EMAIL_ADMIN,
        password="clave-demo-solo-local",
    )
