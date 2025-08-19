
from ftplib import FTP
import logging
import sys

sys.path.append('/var/www/html/config')
from cnxpdo import DB_CONFIG, get_async_connection

logging.basicConfig(level=logging.INFO)


async def consultarPerfiles():
    conn = None
    try:
        conn = await get_async_connection()
        
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT 
                    id,
                    perfiles,
                    descripcion,
                    status,
                    CASE status
                        WHEN 1 THEN 'Activo'
                        WHEN 0 THEN 'Inactivo'
                        ELSE 'Desconocido'
                    END AS nomstatus
                FROM empleados_perfiles
            """)
            
            columns = [col[0] for col in cursor.description]
            perfiles = [dict(zip(columns, row)) for row in await cursor.fetchall()]
            
            return {
                "success": 1,
                "message": "Perfiles encontrados" if perfiles else "No hay perfiles registrados",
                "data": perfiles
            }
            
    except Exception as e:
        logging.error(f"Error en consultarPerfiles: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al consultar perfiles: {str(e)}",
            "data": None
        }
    finally:
        if conn:
            await conn.ensure_closed()

async def insertarPerfil(data: dict):
    conn = None
    try:
        conn = await get_async_connection()
        
        async with conn.cursor() as cursor:
            # 1. Verificar si el perfil ya existe
            await cursor.execute(
                "SELECT COUNT(*) FROM empleados_perfiles WHERE perfiles = %s",
                (data["perfiles"],)
            )
            
            if (await cursor.fetchone())[0] > 0:
                return {
                    "success": 0,
                    "message": "Ya existe un perfil con este nombre",
                    "data": None
                }

            # 2. Insertar nuevo perfil
            await cursor.execute("""
                INSERT INTO empleados_perfiles (perfiles, descripcion, status)
                VALUES (%s, %s, %s)
            """, (data["perfiles"], data.get("descripcion"), data.get("status", 1)))
            
            # 3. Obtener ID del nuevo perfil
            id_insertado = cursor.lastrowid
            
            # 4. Recuperar el perfil creado
            await cursor.execute("""
                SELECT 
                    id,
                    perfiles,
                    descripcion,
                    status
                FROM empleados_perfiles
                WHERE id = %s
            """, (id_insertado,))
            
            columns = [col[0] for col in cursor.description]
            row = await cursor.fetchone()
            
            if not row:
                raise Exception("No se pudo recuperar el perfil recién creado")
            
            perfil = dict(zip(columns, row))
            await conn.commit()
            
            logging.info(f"Perfil creado exitosamente: ID {id_insertado}")
            return {
                "success": 1,
                "message": "Perfil creado exitosamente",
                "data": perfil
            }
            
    except Exception as e:
        logging.error(f"Error en insertarPerfil: {str(e)}", exc_info=True)
        if conn:
            await conn.rollback()
        return {
            "success": 0,
            "message": f"Error al crear perfil: {str(e)}",
            "data": None
        }
    finally:
        if conn:
            await conn.ensure_closed()


async def actualizarPerfil(id_perfil: int, data: dict):
    conn = None
    try:
        conn = await get_async_connection()
        
        async with conn.cursor() as cursor:
            # 1. Verificar si el perfil existe (con tupla correcta)
            await cursor.execute(
                "SELECT COUNT(*) FROM empleados_perfiles WHERE id = %s",
                (id_perfil,) 
            )
            if (await cursor.fetchone())[0] == 0:
                return {
                    "success": 0,
                    "message": "Perfil no encontrado",
                    "data": None
                }

            # 2. Actualizar el perfil (con nombres de columna verificados)
            await cursor.execute("""
                UPDATE empleados_perfiles
                SET perfiles = %s, descripcion = %s, status = %s
                WHERE id = %s
            """, (
                data.get("perfiles"),
                data.get("descripcion"),
                data.get("status", 1),
                id_perfil
            ))
            
            # 3. Obtener los datos actualizados (con nombres de columna consistentes)
            await cursor.execute("""
                SELECT 
                    id, 
                    perfiles,
                    descripcion,
                    status
                FROM empleados_perfiles
                WHERE id = %s
            """, (id_perfil,)) 
            
            columns = [col[0] for col in cursor.description]
            row = await cursor.fetchone()
            
            if not row:
                raise Exception("No se pudo recuperar el perfil actualizado")
            
            perfil_actualizado = dict(zip(columns, row))
            await conn.commit()
            
            return {
                "success": 1,
                "message": "Perfil actualizado exitosamente",
                "data": perfil_actualizado
            }
            
    except Exception as e:
        logging.error(f"Error en actualizarPerfil (ID: {id_perfil}): {str(e)}", exc_info=True)
        if conn:
            await conn.rollback()
        return {
            "success": 0,
            "message": f"Error al actualizar perfil: {str(e)}",
            "data": None
        }
    finally:
        if conn:
            await conn.ensure_closed()


async def eliminarPerfil(id_perfil: int):
    conn = None
    try:
        conn = await get_async_connection()
        
        async with conn.cursor() as cursor:
            # 1. Verificar si el perfil existe en la tabla perfiles
            await cursor.execute(
                "SELECT COUNT(*) FROM empleados_perfiles WHERE id = %s",
                (id_perfil,)
            )
            if (await cursor.fetchone())[0] == 0:
                return {
                    "success": False,
                    "message": "Perfil no encontrado",
                    "data": None
                }

            await cursor.execute(
                "SELECT COUNT(*) FROM permisos WHERE id_perfil = %s",
                (id_perfil)
            )
            count = (await cursor.fetchone())[0]
            
            if count > 0:
                return {
                    "success": 0,
                    "message": "No se puede eliminar: tiene permisos asociados",
                    "data": None
                }

            # 3. Eliminar el perfil de la tabla perfiles
            await cursor.execute(
                "DELETE FROM empleados_perfiles WHERE id = %s",
                (id_perfil,)
            )
            
            # 4. Verificar que se eliminó
            if cursor.rowcount == 0:
                return {
                    "success": False,
                    "message": "No se pudo eliminar el perfil",
                    "data": None
                }
            
            await conn.commit()
            
            return {
                "success": True,
                "message": "Perfil eliminado exitosamente",
                "data": {"id": id}
            }
            
    except Exception as e:
        logging.error(f"Error en eliminarPerfil: {str(e)}", exc_info=True)
        if conn:
            await conn.rollback()
        return {
            "success": 0,
            "message": f"Error al eliminar perfil: {str(e)}",
            "data": None
        }
    finally:
        if conn:
            await conn.ensure_closed()