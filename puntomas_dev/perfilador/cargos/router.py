from fastapi import APIRouter, HTTPException
from perfilador.cargos.model import ( NuevoCargoRequest, ActualizarCargoRequest )
from perfilador.cargos import cargos
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/profiling", tags=["Profiling"])

@router.get("/ask/consultarCargos")
async def consultar_cargos():
    try:
        result = await cargos.consultarCargos()
        return result
    except Exception as e:
        logging.error(f"Error en consultarCargos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/ask/consultarCargo/{id}")
async def get_cargo(id: int):
    try:
        result = await cargos.consultarCargosByAreas(id)
        
        if result["success"] == 0:
            if "no encontrada" in result["message"].lower():
                raise HTTPException(
                    status_code=404,
                    detail=result["message"]
                )
            raise HTTPException(
                status_code=500,
                detail=result["message"]
            )
            
        if not result["data"]:
            raise HTTPException(
                status_code=404,
                detail="No hay cargos en esta área"
            )
            
        return result

    except HTTPException:
        raise
        
    except Exception as e:
        logging.error(f"Error consultando cargos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al consultar cargo"
        )
# Create a new position
@router.post("/ask/newCargos")
async def insertar_cargo(request: NuevoCargoRequest):
    try:
        data = request.dict()
        result = await cargos.insertarCargo(data)
        
        if result["success"] == 0:
            status_code = 400 if "existe" in result["message"] else 500
            raise HTTPException(status_code=status_code, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error crítico al crear cargo: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Update a position
@router.put("/ask/updateCargos/{id}")
async def actualizar_cargo(id: int, request: ActualizarCargoRequest):
    try:
        # Preparamos los datos igual que en actualizar_area
        data = {
            "cargo": request.cargo,
            "descripcion": request.descripcion,
            "idArea": request.idArea
        }

        # Usamos await para llamar a la función asíncrona
        result = await cargos.actualizarCargo(id, data)
        
        if result["success"] == 0:
            raise HTTPException(
                status_code=400 if "requerido" in result["message"].lower() else 404,
                detail=result["message"]
            )
            
        return result

    except HTTPException:
        raise  # Re-lanzamos las excepciones HTTP que ya hayamos capturado
    except Exception as e:
        logging.error(f"Error al actualizar cargo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la solicitud: {str(e)}"
        )

# Delete a position
@router.delete("/ask/deleteCargos/{id_cargo}")
async def delete_cargo(id_cargo: int):
    try:
        result = await cargos.eliminarCargo(id_cargo)
        
        if result["success"] == 0:
            status_code = 400 if "asociados" in result["message"] else 404
            raise HTTPException(
                status_code=status_code,
                detail=result["message"]
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error en endpoint delete_cargo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al eliminar cargo"
        )