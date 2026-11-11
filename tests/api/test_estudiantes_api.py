"""Tests de API: se prueba desde afuera, con peticiones HTTP."""

URL = "/estudiantes"
DATOS = {"nombre": "Ana", "apellido": "Pérez", "email": "ana@example.com"}


def crear_por_api(client, **cambios):
    return client.post(URL, json={**DATOS, **cambios})


def test_post_crea_estudiante_y_responde_201(client):
    response = crear_por_api(client)

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "nombre": "Ana",
        "apellido": "Pérez",
        "email": "ana@example.com",
        "activo": True,
        "nombre_completo": "Ana Pérez",
    }


def test_post_con_email_duplicado_responde_400(client):
    crear_por_api(client)

    response = crear_por_api(client)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Ya existe un estudiante con ese email."
    }


def test_post_con_campo_faltante_responde_422(client):
    response = client.post(URL, json={"nombre": "Ana"})

    assert response.status_code == 422


def test_post_con_campo_extra_responde_422(client):
    response = crear_por_api(client, rol="admin")

    assert response.status_code == 422


def test_post_con_nombre_vacio_responde_422(client):
    response = crear_por_api(client, nombre="")

    assert response.status_code == 422


def test_get_por_id_existente_responde_200(client):
    crear_por_api(client)

    response = client.get(f"{URL}/1")

    assert response.status_code == 200
    assert response.json()["email"] == "ana@example.com"


def test_get_por_id_inexistente_responde_404(client):
    response = client.get(f"{URL}/99")

    assert response.status_code == 404
    assert response.json() == {"detail": "El estudiante no existe."}


def test_get_con_id_cero_responde_422(client):
    assert client.get(f"{URL}/0").status_code == 422


def test_get_lista_con_paginacion_por_defecto(client):
    for i in range(1, 16):
        crear_por_api(client, email=f"e{i}@example.com")

    response = client.get(URL)

    cuerpo = response.json()
    assert response.status_code == 200
    assert cuerpo["total"] == 15
    assert cuerpo["pagina"] == 1
    assert cuerpo["tamano"] == 10
    assert len(cuerpo["items"]) == 10


def test_get_lista_segunda_pagina(client):
    for i in range(1, 16):
        crear_por_api(client, email=f"e{i}@example.com")

    response = client.get(URL, params={"pagina": 2, "tamano": 10})

    assert len(response.json()["items"]) == 5


def test_get_lista_con_tamano_101_responde_422(client):
    assert client.get(URL, params={"tamano": 101}).status_code == 422


def test_get_lista_con_tamano_100_responde_200(client):
    assert client.get(URL, params={"tamano": 100}).status_code == 200


def test_put_actualiza_y_responde_200(client):
    crear_por_api(client)

    response = client.put(
        f"{URL}/1",
        json={**DATOS, "nombre": "Ana María"},
    )

    assert response.status_code == 200
    assert response.json()["nombre_completo"] == "Ana María Pérez"


def test_put_inexistente_responde_404(client):
    assert client.put(f"{URL}/99", json=DATOS).status_code == 404


def test_delete_responde_204_y_luego_404(client):
    crear_por_api(client)

    assert client.delete(f"{URL}/1").status_code == 204
    assert client.get(f"{URL}/1").status_code == 404


def test_delete_inexistente_responde_404(client):
    assert client.delete(f"{URL}/99").status_code == 404
