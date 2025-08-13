from pydantic import BaseModel, validator
from typing import Any, Dict, Union, List, Optional

class InfoClientes(BaseModel):
    id: int
    nombre: str
    email: str
    edad: Optional[int] = None
