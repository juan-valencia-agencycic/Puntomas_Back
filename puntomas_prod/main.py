from fastapi import FastAPI
from clases import InfoClientes
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

