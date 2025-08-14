from pydantic import BaseModel, validator
from typing import Any, Dict, Union, List, Optional

class InfoClientes(BaseModel):
    id: int
    nombre: str
    email: str
    edad: Optional[int] = None

class ObtenerClientePorTelefonoRequest(BaseModel):
    telefonoCli: str
class ClienteRequest(BaseModel):
    telefonoCli: str
    indicador: int
    social: str
class PuntajeRequest(BaseModel):
    telefonoCli: str
    social: str
class DisputasRequest(BaseModel):
    telefonoCli: str
    social: str
class TarjetasRequest(BaseModel):
    telefonoCli: str
    social: str
class PagoRequest(BaseModel):
    telefonoCli: str
    social: str
class CreditInfoRequest(BaseModel):
    telefonoCli: str
    social: str
class DataClienteRequest(BaseModel):
    telefonoCli: str