from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/sms", tags=["sms"])

class SMSRequest(BaseModel):
    id_campana: str

@router.post("/enviar_sms")
async def enviar_sms(request: SMSRequest):
    url = "https://n8n.cic-ware.com/webhook/envioSMS"
    data = {"id_sms": request.id_campana}
    headers = {"Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return {"success": True, "response": response.json()}
            else:
                return {
                    "success": False,
                    "message": "Error al contactar el webhook",
                    "status": response.status_code,
                    "response": response.text
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la petición: {str(e)}")
