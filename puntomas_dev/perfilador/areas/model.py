from pydantic import BaseModel

class NuevoAreaRequest(BaseModel):
    area: str        
    descripcion: str  

class ActualizarAreaRequest(BaseModel):
    area: str
    descripcion: str 