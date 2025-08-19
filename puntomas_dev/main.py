from fastapi import FastAPI, HTTPException, Response, status
import perfilador
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import FileResponse, JSONResponse
import asyncio
import json
from typing import List, Dict, Any
from docs_api import info_clientes_docs
from clientes import info_clientes
from clases import ClienteRequest, ObtenerClientePorTelefonoRequest, PuntajeRequest, DisputasRequest, TarjetasRequest, PagoRequest, CreditInfoRequest, DataClienteRequest, NuevoAreaRequest, ActualizarAreaRequest, ActualizarCargoRequest, NuevoCargoRequest, ActualizarPerfilRequest, NuevoPerfilRequest, ActualizarPermisoRequest, NuevoPermisoRequest, SMSRequest, LdapLoginRequest, PerfilRequest, TokenRequest, PerfilResponse
from perfilador.areas import areas
from perfilador.cargos import cargos
from perfilador.perfiles import perfiles
from perfilador.permisos import permisos
from login.smsmasivo import sms
import httpx
from jose import jwt
from auth.SSO_Ldap import ldap
from auth.SSO_Ldap import credenciales_ldap
from auth.SSO_Microsoft import credenciales_microsoft
from datetime import datetime, timedelta
from auth.SSO_Microsoft.microsoft import verify_microsoft_token, obtener_perfil

# Crear la instancia de la aplicación FastAPI
app = FastAPI()


# origins = [  

# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # Permite estos orígenes
#     allow_credentials=True,
#     allow_methods=["*"],  # Permite todos los métodos, pero puedes restringir si lo deseas
#     allow_headers=["*"],  # Permite todos los encabezados
# )


################################################## PETICIONES GET ######################################################
@app.get("/ask/info-clientes/{id_cliente}", **info_clientes_docs)
async def consultarInfoClientes(id_cliente: int):
    return info_clientes.consultarInfoClientes(id_cliente)

@app.get("/ask/consultarArea")
async def consultar_areas():
    try:
        result = await areas.consultarAreas()  # Usa await sin return aquí
        return result
    except Exception as e:
        logging.error(f"Error en consultarAreas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ask/consultarCargos")
async def consultar_cargos():
    try:
        result = await cargos.consultarCargos()
        return result
    except Exception as e:
        logging.error(f"Error en consultarCargos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ask/consultarCargo/{id}")
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

@app.get("/ask/perfiles", response_model=dict)
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

@app.get("/ask/consultarVistas/{id_modulo}")
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

@app.get("/ask/consultarModulos")
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

@app.get("/ask/consultarPermisosVistas/{idPerfil}")
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

@app.get("/ask/consultarElementos/{id_vista}")
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
@app.get("/ask/consultarElementosPerfil/{id_perfil}")
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
################################################## PETICIONES POSTS ######################################################
@app.post("/ask/obtener-cliente")
async def endpoint_obtener_cliente(request: ObtenerClientePorTelefonoRequest):
    """
    Endpoint que devuelve la info básica del cliente por teléfono.
    """
    try:
        cliente = info_clientes.obtener_cliente_por_telefono(request.telefonoCli)
        if not cliente:
            return JSONResponse(content={"message": "Cliente no encontrado", "cliente": None})
        return JSONResponse(content={"cliente": cliente})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/consultar-cuentas-eliminadas")
async def consultarCuentasEliminadas(request: ClienteRequest):
    try:
        result = info_clientes.consultarCuentasEliminadas(request.telefonoCli, request.indicador, request.social)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/consultar-puntaje")
async def endpoint_consultar_puntaje(request: PuntajeRequest):
    try:
        result = info_clientes.consultar_puntaje_credito(request.telefonoCli, request.social)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/consultar-disputas")
async def endpoint_consultar_disputas(request: DisputasRequest):
    try:
        result = info_clientes.consultar_disputas(request.telefonoCli, request.social)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/consultar-tarjetas")
async def endpoint_consultar_tarjetas(request: TarjetasRequest):
    try:
        result = info_clientes.consultar_tarjetas_aseguradas(request.telefonoCli, request.social)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/consultar-fecha-pago")
async def endpoint_consultar_fecha_pago(request: PagoRequest):
    try:
        result = info_clientes.consultar_fecha_pago(request.telefonoCli, request.social)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/consultar-info-credito")
async def endpoint_consultar_info_credito(request: CreditInfoRequest):
    try:
        result = info_clientes.consultar_info_credito(request.telefonoCli, request.social)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/consultar-info-cliente")
async def endpoint_consultar_info_cliente(request: DataClienteRequest):
    try:
        result = info_clientes.obtener_info_cliente(request.telefonoCli)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud.")

@app.post("/ask/newArea")
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

@app.post("/ask/newCargos")
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

@app.post("/ask/perfiles", response_model=dict)
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

@app.post("/ask/nuevoPermiso")
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

@app.post("/enviar_sms")
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

@app.post("/login")
async def ldap_login(request: LdapLoginRequest, response: Response):
    if ldap.authenticate_ldap(request.username, request.password):
        payload = {
            "user_id": request.username,
            "email": request.username,
            "sesion_activa": 1,
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        jwt_token = jwt.encode(payload, credenciales_ldap.SECRET_KEY, algorithm=credenciales_ldap.ALGORITHM)
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

@app.post("/api/microsoft")
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
        jwt_token = jwt.encode(payload, credenciales_microsoft.SECRET_KEY, algorithm= credenciales_microsoft.ALGORITHM)

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

@app.post("/api/perfil", response_model=PerfilResponse)
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
################################################## PETICIONES PUT ######################################################
@app.put("/ask/updateArea/{id}")
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

@app.put("/ask/updateCargos/{id}")
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

@app.put(
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

@app.put("/ask/actualizarPermiso/{id}")
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
################################################## PETICIONES DELETE ######################################################
@app.delete("/ask/deletearea/{id}")
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

@app.delete("/ask/deleteCargos/{id_cargo}")
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

@app.delete("/ask/perfiles/{id_perfil}")
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

@app.delete("/ask/deletePermissions/{id}")
async def eliminar_permiso(id: int):
    try:
        result = await permisos.eliminarPermiso(id)
        if result["success"] == 0:
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        logging.error(f"Error al eliminar el permiso: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error al procesar la solicitud")