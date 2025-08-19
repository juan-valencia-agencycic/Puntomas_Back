from fastapi import APIRouter, HTTPException
from perfilador.perfiles.model import ( NuevoPerfilRequest, ActualizarPerfilRequest )
from perfilador.perfiles import perfiles
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/profiling", tags=["Profiling"])

@router.get("/ask/perfiles", response_model=dict)
async def get_perfiles():
    try:
        result = await perfiles.consultarPerfiles()
        if result["success"] == 0:
            # Distingue entre errores de cliente y servidor
            status_code = 400 if "validación" in result["message"].lower() else 500
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error en endpoint get_perfiles: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar perfiles"
        )

@router.post("/ask/perfiles", response_model=dict)
async def post_perfil(request: NuevoPerfilRequest):
    try:
        result = await perfiles.insertarPerfil(request.dict())
        if result["success"] == 0:
            raise HTTPException(
                status_code=400 if "existe" in result["message"] else 500,
                detail=result["message"]
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error interno al crear perfil"
        )
        
        
@router.put(
    "/ask/perfiles/{id_perfil}",
    response_model=dict,
)
async def put_perfil(
    id_perfil: int ,
    request: ActualizarPerfilRequest
):
    try:
        result = await perfiles.actualizarPerfil(id_perfil, request.dict())
        
        if result["success"] == 0:
            status_code = 404 if "no encontrado" in result["message"] else 400
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error en endpoint put_perfil: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al actualizar perfil"
        )
        
@router.delete("/ask/perfiles/{id_perfil}")
async def delete_perfil(id_perfil: int):
    try:
        result = await perfiles.eliminarPerfil(id_perfil)
        
        if result["success"]:
            status_code = 200 if "eliminado" in result["message"].lower() else 404
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error en endpoint delete_perfil: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al eliminar perfil"
        )