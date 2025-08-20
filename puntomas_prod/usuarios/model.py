from typing import Optional
from pydantic import BaseModel

class UserData(BaseModel):
    idUser: int
    idEmp: int
    idPerfil: int
    perfil: str
    last_session: str
    nombres: str
    apellidos: str
    tipo_doc: str
    documento: str
    id_cargo: int
    cargo: str
    correo_corporativo: str
    correo_alterno: str
    telefono: str
    direccion: str
    imagen: str
    status: str
    password: str
    passtemp: str
    nomstatus: str