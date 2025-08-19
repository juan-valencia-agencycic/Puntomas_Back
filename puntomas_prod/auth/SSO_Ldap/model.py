from pydantic import BaseModel

class LdapLoginRequest(BaseModel):
    username: str
    password: str