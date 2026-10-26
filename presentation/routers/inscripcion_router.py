from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Response,
    status,
)

from application.services.inscripcion_service import InscripcionService
from presentation.dependencies import (
    get_inscripcion_service,
    get_usuario_actual,
)
from presentation.schemas.dtos.curso_dto import CursoResponseDTO
from presentation.schemas.dtos.estudiante_dto import EstudianteResponseDTO


router = APIRouter(
    tags=["Inscripciones"],
    dependencies=[Depends(get_usuario_actual)],
)

# El servicio se construye por solicitud con su propia sesión de base de datos.
ServiceDep = Annotated[InscripcionService, Depends(get_inscripcion_service)]

EstudianteId = Annotated[int, Path(gt=0)]
CursoId = Annotated[int, Path(gt=0)]


@router.post(
    "/estudiantes/{estudiante_id}/cursos/{curso_id}",
    response_model=CursoResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def inscribir_curso(
    estudiante_id: EstudianteId,
    curso_id: CursoId,
    service: ServiceDep,
):
    try:
        curso = service.inscribir(
            estudiante_id=estudiante_id,
            curso_id=curso_id,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return CursoResponseDTO.model_validate(curso)


@router.get(
    "/estudiantes/{estudiante_id}/cursos",
    response_model=list[CursoResponseDTO],
)
def listar_cursos_de_estudiante(
    estudiante_id: EstudianteId,
    service: ServiceDep,
):
    try:
        cursos = service.cursos_de_estudiante(estudiante_id)
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return [CursoResponseDTO.model_validate(curso) for curso in cursos]


@router.delete(
    "/estudiantes/{estudiante_id}/cursos/{curso_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def retirar_curso(
    estudiante_id: EstudianteId,
    curso_id: CursoId,
    service: ServiceDep,
):
    retirado = service.retirar(
        estudiante_id=estudiante_id,
        curso_id=curso_id,
    )

    if not retirado:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no está inscrito en ese curso.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/cursos/{curso_id}/estudiantes",
    response_model=list[EstudianteResponseDTO],
)
def listar_estudiantes_de_curso(curso_id: CursoId, service: ServiceDep):
    try:
        estudiantes = service.estudiantes_de_curso(curso_id)
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return [
        EstudianteResponseDTO.model_validate(estudiante)
        for estudiante in estudiantes
    ]
