from typing import Optional
from pydantic import BaseModel
from typing import Union

class NuevoPerfilRequest(BaseModel):
    id: int
    perfiles:str
    descripcion: str    
    status: int 
    
class ActualizarPerfilRequest(BaseModel):
    perfiles:str
    descripcion: str    
    status: int 