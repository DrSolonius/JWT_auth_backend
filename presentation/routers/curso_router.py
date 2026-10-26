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

from application.services.curso_service import CursoService
from presentation.dependencies import get_curso_service, get_usuario_actual
from presentation.schemas.dtos.curso_dto import (
    CursoCreateDTO,
    CursoUpdateDTO,
    CursoResponseDTO,
    CursoPaginaDTO,
)

from presentation.schemas.dtos.curso_query_dto import (
    CursoQueryDTO,
)


router = APIRouter(
    prefix="/cursos",
    tags=["Cursos"],
    dependencies=[Depends(get_usuario_actual)],
)

# El servicio se construye por solicitud con su propia sesión de base de datos.
ServiceDep = Annotated[CursoService, Depends(get_curso_service)]

CursoId = Annotated[int, Path(gt=0)]


@router.post(
    "",
    response_model=CursoResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
def crear_curso(datos: CursoCreateDTO, service: ServiceDep):
    try:
        curso = service.crear(
            codigo=datos.codigo,
            nombre=datos.nombre,
            creditos=datos.creditos,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return CursoResponseDTO.model_validate(curso)


@router.get("", response_model=CursoPaginaDTO)
def listar_cursos(
    query: Annotated[CursoQueryDTO, Query()],
    service: ServiceDep,
):
    cursos, total = service.listar(
        pagina=query.pagina,
        tamano=query.tamano,
    )

    return CursoPaginaDTO(
        items=[
            CursoResponseDTO.model_validate(curso)
            for curso in cursos
        ],
        total=total,
        pagina=query.pagina,
        tamano=query.tamano,
    )


@router.get(
    "/{curso_id}",
    response_model=CursoResponseDTO,
)
def obtener_curso(curso_id: CursoId, service: ServiceDep):
    curso = service.obtener(curso_id)

    if curso is None:
        raise HTTPException(
            status_code=404,
            detail="El curso no existe.",
        )

    return CursoResponseDTO.model_validate(curso)


@router.put(
    "/{curso_id}",
    response_model=CursoResponseDTO,
)
def actualizar_curso(
    curso_id: CursoId,
    datos: CursoUpdateDTO,
    service: ServiceDep,
):
    try:
        curso = service.actualizar(
            curso_id=curso_id,
            codigo=datos.codigo,
            nombre=datos.nombre,
            creditos=datos.creditos,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if curso is None:
        raise HTTPException(
            status_code=404,
            detail="El curso no existe.",
        )

    return CursoResponseDTO.model_validate(curso)


@router.delete(
    "/{curso_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_curso(curso_id: CursoId, service: ServiceDep):
    eliminado = service.eliminar(curso_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="El curso no existe.",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
