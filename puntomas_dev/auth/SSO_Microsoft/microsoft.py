from jose import jwt
from jose.exceptions import JWTError
import requests
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys

sys.path.append('/var/www/html/config')
from cnxpdo import DB_CONFIG, get_async_connection, get_async_connection_puntomasv3, DB_CONFIG_PUNTOMASV3
from auth.SSO_Microsoft.model import (PerfilResponse, PerfilRequest)

security = HTTPBearer()

def get_microsoft_public_key(kid: str) -> Optional[Dict[str, Any]]:
    """Obtiene la clave pública específica de Microsoft para un kid dado"""
    jwks_url = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
    try:
        response = requests.get(jwks_url)
        jwks = response.json()
        for key in jwks["keys"]:
            if key["kid"] == kid:
                return key
        return None
    except Exception as e:
        print(f"Error al obtener claves públicas: {str(e)}")
        return None

def verify_microsoft_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        print("Iniciando verificación de token...")

        # 1. Obtener el header sin validar para extraer el kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            print("Token no contiene kid en el header")
            return None

        # 2. Obtener la clave pública correspondiente
        public_key_info = get_microsoft_public_key(kid)
        if not public_key_info:
            print(f"No se encontró clave pública para kid: {kid}")
            return None

        # 3. Validar el token usando el JWK directamente
        payload = jwt.decode(
            token,
            public_key_info,
            algorithms=["RS256"],
            audience="4a6d6cf7-bf35-4e06-95bf-cd28e0d29950",
            issuer="https://login.microsoftonline.com/6cdfbc33-3f56-4134-822c-e24936dea384/v2.0"
        )

        print("Token validado correctamente", payload)
        return payload

    except JWTError as e:
        print(f"Error de validación JWT: {str(e)}")
        return None
    except Exception as e:
        print(f"Error inesperado al validar token: {str(e)}")
        return None

async def obtener_perfil(perfil_request: PerfilRequest) -> PerfilResponse:
    """Función para obtener perfil de usuario desde la base de datos"""
    print("Iniciando obtención de perfil...")
    
    correo = perfil_request.correo
    if not correo:
        raise HTTPException(status_code=400, detail="Correo requerido")

    print(f"Buscando perfil para correo: {correo}")

    conn_v3 = None
    conn_v4 = None
    try:
        conn_v3 = await get_async_connection_puntomasv3()
        
        async with conn_v3.cursor() as cursor:
            print(f"Ejecutando consulta: SELECT id_perfil FROM usertbl WHERE email = '{correo}'")
            
            await cursor.execute(
                "SELECT idPerfil FROM usertbl WHERE email = %s", 
                (correo,)
            )
            row = await cursor.fetchone()
            
            if not row:
                print(f"No se encontró usuario con correo: {correo}")
                raise HTTPException(status_code=404, detail="Usuario no registrado")
            
            id_perfil = row[0]
            print(f"ID de perfil encontrado: {id_perfil}")

        conn_v4 = await get_async_connection()
        
        async with conn_v4.cursor() as cursor:
            print(f"Ejecutando consulta: SELECT perfiles FROM empleados_perfiles WHERE id = {id_perfil}")
            
            await cursor.execute(
                "SELECT perfiles FROM empleados_perfiles WHERE id = %s", 
                (id_perfil,)
            )
            perfil_row = await cursor.fetchone()
            
            if not perfil_row:
                print(f"No se encontró perfil con ID: {id_perfil}")
                raise HTTPException(status_code=404, detail="Perfil no encontrado")

            perfil = perfil_row[0]
            print(f"Perfil encontrado: {perfil}")

        return PerfilResponse(
            correo=correo,
            id_perfil=id_perfil,
            perfil=perfil
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en consulta de base de datos: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al consultar la base de datos: {str(e)}"
        )
    finally:
        if conn_v3:
            await conn_v3.ensure_closed()
        if conn_v4:
            await conn_v4.ensure_closed()