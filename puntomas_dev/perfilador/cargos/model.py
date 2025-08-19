from pydantic import BaseModel

class NuevoCargoRequest(BaseModel):
    cargo: str
    descripcion: str
    idArea: int

class ActualizarCargoRequest(BaseModel):
    cargo: str
    descripcion: str
    idArea: int