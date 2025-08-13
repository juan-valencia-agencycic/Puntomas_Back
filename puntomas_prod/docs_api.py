info_clientes_docs = {
    "summary": "Consultar configuración de cuenta de servicios",
    "description": """
Consulta los datos de configuración asociados a una cuenta de servicios específica mediante su ID.
La respuesta está codificada en Base64 para garantizar la seguridad de los datos.
Este servicio es usado al momento de validar la configuración técnica del canal de afiliación.
""",
    "response_description": "Respuesta exitosa con datos encriptados en Base64.",
    "responses": {
        200: {
            "description": "Cuentas obtenidas exitosamente.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Respuesta encriptada en Base64",
                        "data": "ZXhhbXBsbyBlbiBiYXNlNjQ="
                    }
                }
            }
        },
        404: {
            "description": "Cuenta no encontrada.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "No se encontró la cuenta de servicios con el ID proporcionado."
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Error: No se pudo consultar la cuenta por un fallo interno."
                    }
                }
            }
        }
    }
}
