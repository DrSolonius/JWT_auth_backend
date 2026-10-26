from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)

from application.services.estudiante_service import EstudianteService
from presentation.dependencies import (
    get_estudiante_service,
    get_usuario_actual,
)
from presentation.schemas.dtos.estudiante_dto import (
    EstudianteCreateDTO,
    EstudianteUpdateDTO,
    EstudianteResponseDTO,
    EstudiantePaginaDTO,
)

from presentation.schemas.dtos.estudiante_query_dto import (
    EstudianteQueryDTO,
)


router = APIRouter(
    prefix="/estudiantes",
    tags=["Estudiantes"],
    dependencies=[Depends(get_usuario_actual)],
)

# El servicio se construye por solicitud con su propia sesión de base de datos.
ServiceDep = Annotated[EstudianteService, Depends(get_estudiante_service)]

EstudianteId = Annotated[int, Path(gt=0)]


@router.post(
    "",
    response_model=EstudianteResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def crear_estudiante(datos: EstudianteCreateDTO, service: ServiceDep):
    try:
        estudiante = service.crear(
            nombre=datos.nombre,
            apellido=datos.apellido,
            email=datos.email,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return EstudianteResponseDTO.model_validate(estudiante)


@router.get("", response_model=EstudiantePaginaDTO)
def listar_estudiantes(
    query: Annotated[EstudianteQueryDTO, Query()],
    service: ServiceDep,
):
    estudiantes, total = service.listar(
        pagina=query.pagina,
        tamano=query.tamano,
    )

    return EstudiantePaginaDTO(
        items=[
            EstudianteResponseDTO.model_validate(estudiante)
            for estudiante in estudiantes
        ],
        total=total,
        pagina=query.pagina,
        tamano=query.tamano,
    )


@router.get(
    "/{estudiante_id}",
    response_model=EstudianteResponseDTO,
)
def obtener_estudiante(estudiante_id: EstudianteId, service: ServiceDep):
    estudiante = service.obtener(estudiante_id)

    if estudiante is None:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no existe.",
        )

    return EstudianteResponseDTO.model_validate(estudiante)


@router.put(
    "/{estudiante_id}",
    response_model=EstudianteResponseDTO,
)
def actualizar_estudiante(
    estudiante_id: EstudianteId,
    datos: EstudianteUpdateDTO,
    service: ServiceDep,
):
    try:
        estudiante = service.actualizar(
            estudiante_id=estudiante_id,
            nombre=datos.nombre,
            apellido=datos.apellido,
            email=datos.email,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if estudiante is None:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no existe.",
        )

    return EstudianteResponseDTO.model_validate(estudiante)


@router.delete(
    "/{estudiante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_estudiante(estudiante_id: EstudianteId, service: ServiceDep):
    eliminado = service.eliminar(estudiante_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no existe.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)