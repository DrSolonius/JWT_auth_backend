class ErrorAutenticacion(Exception):
    """Base de los errores de autenticación: la presentación los traduce a 401."""


class CredencialesInvalidas(ErrorAutenticacion):
    pass


class CuentaBloqueada(ErrorAutenticacion):
    pass


class TokenInvalido(ErrorAutenticacion):
    pass
