from pydantic import BaseModel

class TokenRequest(BaseModel):
    token: str
    
class PerfilRequest(BaseModel):
    correo: str
    
class PerfilResponse(BaseModel):
    correo: str
    id_perfil: int
    perfil: str