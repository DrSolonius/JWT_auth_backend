"""Tests de API del acceso: los endpoints protegidos exigen un token JWT.

Aquí NO se reemplaza get_usuario_actual: se prueba la autenticación real.
"""

URL = "/estudiantes"
CREDENCIALES = {"email": "docente@example.com", "password": "clave-de-prueba"}


def test_sin_token_responde_401(client_sin_login):
    response = client_sin_login.get(URL)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_token_invalido_responde_401(client_sin_login):
    response = client_sin_login.get(
        URL, headers={"Authorization": "Bearer token-falso"}
    )

    assert response.status_code == 401


def test_login_con_clave_incorrecta_responde_401(client_sin_login):
    client_sin_login.post("/auth/registro", json=CREDENCIALES)

    response = client_sin_login.post(
        "/auth/login", json={**CREDENCIALES, "password": "otra-clave"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales inválidas."}


def test_registro_login_y_acceso_con_token(client_sin_login):
    registro = client_sin_login.post("/auth/registro", json=CREDENCIALES)
    assert registro.status_code == 201

    login = client_sin_login.post("/auth/login", json=CREDENCIALES)
    assert login.status_code == 200
    token = login.json()["access_token"]

    response = client_sin_login.get(
        URL, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0
