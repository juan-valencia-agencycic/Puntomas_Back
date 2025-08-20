from fastapi import APIRouter, HTTPException, status, Response, Request,  Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime, timedelta
from jose import jwt
from auth.SSO_Microsoft.model import (TokenRequest, PerfilRequest, PerfilResponse)
from auth.SSO_Microsoft.microsoft import verify_microsoft_token, obtener_perfil

router = APIRouter(prefix="/auth", tags=["SSO-Microsoft"])
security = HTTPBearer()

SECRET_KEY = "TU_CLAVE_SECRETA"
ALGORITHM = "HS256"

@router.post("/api/microsoft")
async def microsoft_login(request: TokenRequest, response: Response):
    try:
        # 1. Verificar el token de Microsoft
        user_info = verify_microsoft_token(request.token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de Microsoft inválido",
            )

        # 2. Extraer información del usuario con manejo seguro
        user_id = user_info.get("oid") or user_info.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token no contiene identificador de usuario",
            )

        unique_name = user_info.get("unique_name") or user_info.get("preferred_username", "")

        # 3. Crear JWT propio
        payload = {
            "user_id": user_id,
            "email": unique_name,
            "sesion_activa": 1,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # 4. Poner el JWT en una cookie HTTP Only
        response.set_cookie(
            key="sso_token_microsoft",
            value=jwt_token,
            httponly=True,
            secure=True,  # True en producción con HTTPS
            samesite="lax",
            domain=".credimas.us"   # Descomenta para usar dominios
        )
        return {"ok": True}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error interno: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
            headers={"Access-Control-Allow-Origin": "http://localhost:4200"}
        )

@router.post("/api/perfil", response_model=PerfilResponse)
async def obtener_perfil_route(perfil_request: PerfilRequest):
    try:
        return await obtener_perfil(perfil_request)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error interno: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
            headers={"Access-Control-Allow-Origin": "http://localhost:4200"}
        )