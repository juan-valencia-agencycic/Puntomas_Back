import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importa el middleware CORS

# Importar routers
from perfilador.areas.router import router as areas_router
from perfilador.cargos.router import router as cargos_router
from perfilador.perfiles.router import router as perfiles_router
from perfilador.permisos.router import router as permisos_router
from botmaker.botprincipal.router import router as bot_router

# Ruta para auth SSO Microsoft, enviar token para cookie
from auth.SSO_Microsoft.router import router as microsoft_router
from auth.SSO_Ldap.router import router as ldap_router
app = FastAPI()
     
# Configuración CORS (agrega esto antes de incluir los routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://puntomas.credimas.us", "http://localhost:4200"],  # Permite todos los orígenes
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
    allow_credentials=True
)

#Rutas del perfilador 
app.include_router(areas_router)
app.include_router(cargos_router)
app.include_router(perfiles_router)
app.include_router(permisos_router)

# SSO RUTAS
app.include_router(microsoft_router)
app.include_router(ldap_router)

# Rutas del botmaker
app.include_router(bot_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile=None,
        ssl_certfile=None
    )