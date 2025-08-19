from fastapi import APIRouter, HTTPException, Response
from datetime import datetime, timedelta
from jose import jwt
from .model import LdapLoginRequest
from .ldap import authenticate_ldap

SECRET_KEY = "TU_CLAVE_SECRETA"
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth/ldap", tags=["SSO-LDAP"])

@router.post("/login")
async def ldap_login(request: LdapLoginRequest, response: Response):
    if authenticate_ldap(request.username, request.password):
        payload = {
            "user_id": request.username,
            "email": request.username,
            "sesion_activa": 1,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        print("JWT generado de logueo en ldap es:", jwt_token)
        response.set_cookie(
            key="sso_token_ldap",
            value=jwt_token,
            httponly=True,
            secure=False,  # True si esta en producción
            samesite="lax",
            # domain=".credimas.us"  # Descomenta para usar dominios
        )
        return {"message": "Login exitoso"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")