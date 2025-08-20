from pydantic import BaseModel
from typing import Optional

class NuevoPermisoRequest(BaseModel):
    id_perfil: int
    id_modulo: int
    id_vista: int
    id_elemento: Optional[int]
    permiso: str

class ActualizarPermisoRequest(BaseModel):
    id_perfil: int
    id_modulo: int
    id_vista: int
    id_elemento: Optional[int]
    permiso: str