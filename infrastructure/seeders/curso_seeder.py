from application.services.curso_service import CursoService


def seed_cursos(service: CursoService) -> None:
    """Carga 10 cursos de prueba en el repositorio en memoria."""

    cursos = [
        {"codigo": "INF101", "nombre": "Introducción a la Programación", "creditos": 6},
        {"codigo": "INF102", "nombre": "Programación Orientada a Objetos", "creditos": 6},
        {"codigo": "INF201", "nombre": "Estructuras de Datos", "creditos": 6},
        {"codigo": "INF202", "nombre": "Bases de Datos", "creditos": 6},
        {"codigo": "INF203", "nombre": "Desarrollo Backend", "creditos": 5},
        {"codigo": "INF204", "nombre": "Desarrollo Frontend", "creditos": 5},
        {"codigo": "INF301", "nombre": "Ingeniería de Software", "creditos": 6},
        {"codigo": "INF302", "nombre": "Redes de Computadores", "creditos": 5},
        {"codigo": "MAT101", "nombre": "Cálculo I", "creditos": 6},
        {"codigo": "MAT102", "nombre": "Álgebra Lineal", "creditos": 5},
    ]

    for datos in cursos:
        service.crear(
            codigo=datos["codigo"],
            nombre=datos["nombre"],
            creditos=datos["creditos"],
        )
