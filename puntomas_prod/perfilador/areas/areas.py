
from ftplib import FTP
import asyncmy
import logging

logging.basicConfig(level=logging.INFO)

class DatabaseError(Exception):
    """Clase personalizada para errores de base de datos"""
    pass

# Configuración centralizada de la base de datos
DB_CONFIG = {
    "host": "dev-puntomas.credimas.us",
    "user": "puntomas",
    "password": "u2$p1Lg@XY#XUpY2kf",
    "database": "puntomas2",
}

async def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    try:
        return await asyncmy.connect(**DB_CONFIG)
    except Exception as e:
        logging.error(f"Error de conexión a la base de datos: {str(e)}")
        raise DatabaseError("No se pudo conectar a la base de datos")

async def execute_query(query, params=None):
    """Ejecuta una consulta y devuelve los resultados"""
    conn = None
    try:
        conn = await get_db_connection()
        async with conn.cursor() as cursor:
            await cursor.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                return await cursor.fetchall()
            await conn.commit()
            return True
    except Exception as e:
        logging.error(f"Error en la consulta: {str(e)}")
        raise DatabaseError(f"Error en la operación de base de datos: {str(e)}")
    finally:
        if conn:
            await conn.ensure_closed()

async def consultarAreas():
    try:
        areas = await execute_query("SELECT * FROM empleados_areas")
        return {
            "success": 1,
            "message": "Áreas encontradas" if areas else "No hay áreas registradas",
            "data": areas or []
        }
    except DatabaseError as e:
        return {"success": 0, "message": str(e), "data": []}

async def insertarArea(data):
    try:
        await execute_query(
            "INSERT INTO empleados_areas (area, descripcion) VALUES (%s, %s)",
            (data["area"], data["descripcion"])
        )
        return {
            "success": 1,
            "message": "Área insertada",
            "data": data
        }
    except DatabaseError as e:
        return {"success": 0, "message": str(e)}

async def actualizarArea(id, data):
    try:
        # Primero verificar si el área existe
        check_result = await execute_query(
            "SELECT id FROM empleados_areas WHERE id = %s",
            (id,)
        )
        
        if not check_result:
            return {
                "success": 0,
                "message": "Área no encontrada",
                "data": []
            }

        # Si existe, proceder con la actualización
        await execute_query(
            "UPDATE empleados_areas SET area = %s, descripcion = %s WHERE id = %s",
            (data["area"], data["descripcion"], id)
        )
        return {
            "success": 1,
            "message": "Área actualizada",
            "data": {**data, "id": id}
        }
    except DatabaseError as e:
        return {"success": 0, "message": str(e), "data": []}

async def eliminarArea(id):
    conn = None
    try:
        conn = await asyncmy.connect(**DB_CONFIG)
        
        async with conn.cursor() as cursor:
            # Primero verificar si el área existe
            await cursor.execute("SELECT id FROM empleados_areas WHERE id = %s", (id,))
            if not await cursor.fetchone():
                return {
                    "success": 0,
                    "message": "Área no encontrada"
                }

            # Verificar cargos asociados
            await cursor.execute("""
                SELECT COUNT(*) 
                FROM empleados_cargos 
                WHERE idArea = %s
                """, (id,))
            count = (await cursor.fetchone())[0]

            if count > 0:
                return {
                    "success": 0,
                    "message": "No se puede eliminar el área porque tiene cargos asociados"
                }
            
            # Eliminar área
            await cursor.execute("""
                DELETE FROM empleados_areas 
                WHERE id = %s
                """, (id,))
            await conn.commit()

            return {
                "success": 1,
                "message": "Área eliminada correctamente"
            }

    except Exception as e:
        logging.error(f"Error al eliminar área: {str(e)}")
        return {
            "success": 0,
            "message": f"Error de base de datos: {str(e)}"
        }
    finally:
        if conn:
            await conn.ensure_closed()