from fastapi import APIRouter, HTTPException
from perfilador.permisos.model import ( NuevoPermisoRequest, ActualizarPermisoRequest )
from perfilador.permisos import permisos
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/profiling", tags=["Profiling"])

@router.get("/ask/consultarPermisos/{id_perfil}")
async def get_permisos(id_perfil: int):
    try:
        result = await permisos.consultarPermisos(id_perfil)
        if result["success"] == 0:
            raise HTTPException(
                status_code=404 if "no hay" in result["message"].lower() else 400,
                detail=result["message"]
            )
        return result
    except Exception as e:
        logging.error(f"Error en el endpoint consultar_permisos: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar permisos"
        )

# RUTAS PARA VISTAS
# Get all views
@router.get("/ask/consultarVistas/{id_modulo}")
async def consultar_vistas(id_modulo: int):
    try:
        result = await permisos.consultarVistas(id_modulo)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])  
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error al consultar las vistas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")

# Get all modules (used for views hierarchy)
@router.get("/ask/consultarModulos")
async def consultar_modulos():
    try:
        result = await permisos.consultarModulos()
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error al consultar los módulos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")
        
# Get permissions by view (for a profile)
@router.get("/ask/consultarPermisosVistas/{idPerfil}")
async def get_permisos_vistas(idPerfil: int):
    try:
        result = await permisos.consultarPermisosVistas(idPerfil)
        if result["success"] == 0:
            raise HTTPException(
                status_code=404 if "no se encontraron" in result["message"].lower() else 400,
                detail=result["message"]
            )
        return result
    except Exception as e:
        logging.error(f"Error en el endpoint consultar_permisos_vistas: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar permisos de vistas"
        )

@router.get("/ask/consultarElementos/{id_vista}")
async def consultar_elementos(id_vista: int):
    try:
        result = await permisos.consultarElementos(id_vista)
        if result["success"] == 0:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error al consultar los elementos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")

# Get elements assigned to a profile
@router.get("/ask/consultarElementosPerfil/{id_perfil}")
async def consultar_elementos_perfil(id_perfil: int):
    try:
        result = await permisos.consultarPermisosElementos(id_perfil)
        if result["success"] == 0:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error al consultar los permisos del perfil: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")
# Create a new permission
@router.post("/ask/nuevoPermiso")
async def insertar_permiso(request: NuevoPermisoRequest):
    try:
        data = request.dict()
        result = await permisos.insertarPermiso(data)
        if result["success"] == 0:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logging.error(f"Error al insertar el permiso: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")

# Update a permission
@router.put("/ask/actualizarPermiso/{id}")
async def actualizar_permiso(id: int, request: ActualizarPermisoRequest):
    try:
        data = request.dict()
        result = await permisos.actualizarPermiso(id, data)
        if result["success"] == 0:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        logging.error(f"Error al actualizar el permiso: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")

# Delete a permission
@router.delete("/ask/deletePermissions/{id}")
async def eliminar_permiso(id: int):
    try:
        result = await permisos.eliminarPermiso(id)
        if result["success"] == 0:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        logging.error(f"Error al eliminar el permiso: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")
    
