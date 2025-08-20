from pydantic import BaseModel, validator
from typing import Any, Dict, Union, List, Optional


##### CLASES CLIENTES/INFO-CLIENTES #####
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

##### CLASES AUTH/SSO LDAP  #####
class LdapLoginRequest(BaseModel):
    username: str
    password: str

##### CLASES AUTH/SSO MICROSOFT #####
class TokenRequest(BaseModel):
    token: str
    
class PerfilRequest(BaseModel):
    correo: str
    
class PerfilResponse(BaseModel):
    correo: str
    id_perfil: int
    perfil: str
    
##### CLASES PERFILADOR/AREAS #####
class NuevoAreaRequest(BaseModel):
    area: str        
    descripcion: str  

class ActualizarAreaRequest(BaseModel):
    area: str
    descripcion: str 
    
###### CLASES PERFILADOR/CARGOS ######
class NuevoCargoRequest(BaseModel):
    cargo: str
    descripcion: str
    idArea: int

class ActualizarCargoRequest(BaseModel):
    cargo: str
    descripcion: str
    idArea: int
    
###### CLASES PERFILADOR/PERFILES ######
class NuevoPerfilRequest(BaseModel):
    id: int
    perfiles:str
    descripcion: str    
    status: int 
    
class ActualizarPerfilRequest(BaseModel):
    perfiles:str
    descripcion: str    
    status: int
    
###### CLASES PERFILADOR/PERMISOS ######
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
    
###### CLASES USUARIOS/USUARIOS ######
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

##### CLASES DE LOGIN/SMS #####
class SMSRequest(BaseModel):
    id_campana: str
    
##### CLASES DE ERRORES #####
class DatabaseError(Exception):
    """Clase personalizada para errores de base de datos"""
    pass