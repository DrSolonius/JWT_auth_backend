from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from application.services.usuario_service import UsuarioService
from presentation.dependencies import (
    AdminActualDep,
    get_admin_actual,
    get_usuario_service,
)
from presentation.schemas.dtos.auth_dto import UsuarioResponseDTO


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(get_admin_actual)],
)

UsuarioServiceDep = Annotated[UsuarioService, Depends(get_usuario_service)]


@router.get("", response_model=list[UsuarioResponseDTO])
def listar_usuarios(service: UsuarioServiceDep, activo: bool | None = None):
    """Con ?activo=false lista las cuentas pendientes de aprobación."""
    return [UsuarioResponseDTO.model_validate(u) for u in service.listar(activo)]


@router.post("/{usuario_id}/activar", response_model=UsuarioResponseDTO)
def activar_usuario(usuario_id: int, service: UsuarioServiceDep):
    try:
        usuario = service.activar(usuario_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return UsuarioResponseDTO.model_validate(usuario)


@router.post("/{usuario_id}/desactivar", response_model=UsuarioResponseDTO)
def desactivar_usuario(
    usuario_id: int,
    admin: AdminActualDep,
    service: UsuarioServiceDep,
):
    try:
        usuario = service.desactivar(usuario_id, admin.id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return UsuarioResponseDTO.model_validate(usuario)
