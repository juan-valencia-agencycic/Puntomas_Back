from fastapi import APIRouter, HTTPException
from perfilador.areas.model import ( NuevoAreaRequest, ActualizarAreaRequest )
from perfilador.areas import areas
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/profiling", tags=["Profiling"])

@router.get("/ask/consultarArea")
async def consultar_areas():
    try:
        result = await areas.consultarAreas()  # Usa await sin return aquí
        return result
    except Exception as e:
        logging.error(f"Error en consultarAreas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask/newArea")
async def insertar_area(request: NuevoAreaRequest):
    try:
        data = {
            "area": request.area,
            "descripcion": request.descripcion
        }
        # Añade await y maneja el resultado
        result = await areas.insertarArea(data)
        if result["success"] == 0:
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logging.error(f"Error al insertar área: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/ask/updateArea/{id}")
async def actualizar_area(id: int, request: ActualizarAreaRequest):
    try:
        data = {
            "area": request.area,
            "descripcion": request.descripcion
        }

        result = await areas.actualizarArea(id, data)
        
        if result["success"] == 0:
            if "no encontrada" in result["message"].lower():
                raise HTTPException(status_code=404, detail="Área no encontrada")
            raise HTTPException(
                status_code=400 if "asociados" in result["message"] else 500,
                detail=result["message"]
            )
        return result

    except Exception as e:
        logging.error(f"Error al actualizar área: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ask/deletearea/{id}")
async def eliminar_area(id: int):
    try:
        result = await areas.eliminarArea(id)
        
        if result["success"] == 0:
            if "no encontrada" in result["message"].lower():
                raise HTTPException(status_code=404, detail="Área no encontrada")
            raise HTTPException(
                status_code=400 if "asociados" in result["message"] else 500,
                detail=result["message"]
            )
        return result

    except Exception as e:
        logging.error(f"Error al eliminar área: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))