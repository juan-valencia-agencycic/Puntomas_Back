from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import asyncio
import json
from typing import List, Dict, Any
from docs_api import info_clientes_docs
from clientes import info_clientes
from clases import ClienteRequest, ObtenerClientePorTelefonoRequest, PuntajeRequest, DisputasRequest, TarjetasRequest, PagoRequest, CreditInfoRequest, DataClienteRequest

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