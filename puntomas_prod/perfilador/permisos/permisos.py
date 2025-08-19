from ftplib import FTP
from cnxpdo import DB_CONFIG, get_async_connection
# from dotenv import load_dotenv
# Cargar las variables de entorno desde el archivo .env

import logging

logging.basicConfig(level=logging.INFO)

async def consultarPermisosVistas(id_perfil: int):
    conn = None
    try:
        # 1. Establecer conexión
        conn = await get_async_connection()
        
        # 2. Ejecutar consulta
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT p.*, m.modulo, mv.nombre_vista AS vista 
                FROM permisos p 
                INNER JOIN modulos m ON p.id_modulo = m.id 
                INNER JOIN modulos_vistas mv ON p.id_vista = mv.id 
                WHERE p.id_perfil = %s
                AND (p.id_elemento IS NULL OR p.id_elemento = 0 OR p.id_elemento = '' OR p.id_elemento = 'NULL')
            """, (id_perfil,))
            
            # 3. Convertir resultados a diccionario
            columns = [col[0] for col in cursor.description]
            permisos_vistas = [dict(zip(columns, row)) for row in await cursor.fetchall()]
            
            # 4. Validación (opcional, puedes agregar más si quieres)
            for permiso in permisos_vistas:
                if not permiso.get('vista'):
                    logging.warning(f"Permiso ID {permiso.get('id')} para perfil {id_perfil} no tiene vista asignada")
            
            # 5. Retornar resultados
            return {
                "success": 1,
                "message": "Permisos encontrados" if permisos_vistas else "No se encontraron permisos de vistas para este perfil",
                "data": permisos_vistas,
            }
            
    except Exception as e:
        logging.error(f"Error al consultar permisos vistas para perfil {id_perfil}: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al consultar permisos vistas: {str(e)}",
            "data": []
        }
    finally:
        if conn:
            await conn.ensure_closed()


async def consultarPermisos(id_perfil: int):
    conn = None
    try:
        # 1. Establecer conexión
        conn = await get_async_connection()
        
        # 2. Ejecutar consulta
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT p.*, m.modulo, mv.nombre_vista AS vista, pe.elemento 
                FROM permisos p 
                INNER JOIN modulos m ON p.id_modulo = m.id 
                INNER JOIN modulos_vistas mv ON p.id_vista = mv.id 
                LEFT JOIN permisos_elementos pe ON pe.id = p.id_elemento 
                WHERE p.id_perfil = %s
            """, (id_perfil,))
            
            # 3. Convertir resultados a diccionario
            columns = [col[0] for col in cursor.description]
            permisos = [dict(zip(columns, row)) for row in await cursor.fetchall()]
            
            # 4. Validación de datos (ejemplo: puedes agregar más)
            for permiso in permisos:
                if not permiso.get('modulo'):
                    logging.warning(f"Permiso ID {permiso.get('id')} para perfil {id_perfil} no tiene módulo")
                if permiso.get('elemento') and len(permiso['elemento']) > 255:
                    logging.warning(f"Permiso ID {permiso.get('id')} tiene elemento largo")
            
            # 5. Retornar resultados
            return {
                "success": 1,
                "message": "Permisos encontrados" if permisos else "No hay permisos para este perfil",
                "data": permisos,
            }
            
    except Exception as e:
        logging.error(f"Error al consultar permisos para perfil {id_perfil}: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al consultar permisos: {str(e)}",
            "data": []
        }
    finally:
        if conn:
            await conn.ensure_closed()


async def consultarPermisosElementos(id_perfil: int):
    conn = None
    try:
        conn = await get_async_connection()
        async with conn.cursor() as cursor:
            query = """
                SELECT p.*, m.modulo, mv.nombre_vista AS vista, pe.elemento AS elemento 
                FROM permisos p 
                INNER JOIN modulos m ON p.id_modulo = m.id 
                INNER JOIN modulos_vistas mv ON p.id_vista = mv.id 
                INNER JOIN permisos_elementos pe ON p.id_elemento = pe.id 
                WHERE p.id_perfil = %s
            """
            await cursor.execute(query, (id_perfil,))
            result = await cursor.fetchall()
            
            if result:
                columns = [desc[0] for desc in cursor.description]
                data = [dict(zip(columns, row)) for row in result]
                return {
                    "success": 1,
                    "message": "Permisos encontrados",
                    "data": data
                }
            else:
                return {
                    "success": 0,
                    "message": "No se encontraron permisos para ese perfil",
                    "data": []
                }

    except Exception as e:
        logging.error(f"Error al consultar permisos del perfil: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al consultar permisos del perfil: {str(e)}",
            "data": []
        }
    finally:
        if conn:
            await conn.ensure_closed()



async def consultarModulos():
    conn = None
    try:
        # Conectar a la base de datos de forma asíncrona
        conn = await get_async_connection()
        async with conn.cursor() as cursor:
            query = "SELECT * FROM modulos"
            await cursor.execute(query)
            result = await cursor.fetchall()

            if result:
                # Obtener los nombres de las columnas
                columns = [desc[0] for desc in cursor.description]
                # Convertir cada fila en un diccionario
                data = [dict(zip(columns, row)) for row in result]
                return {
                    "success": True,
                    "message": "Módulos encontrados",
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontraron módulos",
                    "data": []
                }

    except Exception as e:
        logging.error(f"Error al consultar módulos: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error al consultar módulos: {str(e)}",
            "data": []
        }

    finally:
        if conn:
            await conn.ensure_closed()

async def consultarVistas(id_modulo: int):
    conn = None
    try:
        # Conectar a la base de datos de forma asíncrona
        conn = await get_async_connection()
        async with conn.cursor() as cursor:
            query = "SELECT * FROM modulos_vistas WHERE id_modulo = %s"
            await cursor.execute(query, (id_modulo,))
            result = await cursor.fetchall()

            if result:
                # Obtener los nombres de las columnas
                columns = [desc[0] for desc in cursor.description]
                # Convertir cada fila en un diccionario
                data = [dict(zip(columns, row)) for row in result]
                return {
                    "success": True,
                    "message": "Vistas encontradas",
                    "data": data
                }
            else:
                return {
                    "success": False,
                    "message": "No se encontraron vistas",
                    "data": []
                }

    except Exception as e:
        logging.error(f"Error al consultar vistas por id_modulo: {str(e)}", exc_info=True)
        return {
            "success": False,
            "message": f"Error al consultar vistas: {str(e)}",
            "data": []
        }

    finally:
        if conn:
            await conn.ensure_closed()
        
        
async def consultarElementos(id_vista: int):
    """
    Consulta los elementos de permisos asociados a una vista específica.
    
    Args:
        id_vista (int): El ID de la vista para la cual se consultarán los elementos
    
    Returns:
        dict: Un diccionario con:
            - success (int): 1 si fue exitoso, 0 si hubo error
            - message (str): Mensaje descriptivo del resultado
            - data (list): Lista de elementos encontrados
    """
    conn = None
    try:
        # Validar que el id_vista sea un número positivo
        if not isinstance(id_vista, int) or id_vista <= 0:
            return {
                "success": 0,
                "message": "El ID de vista debe ser un número entero positivo",
                "data": []
            }

        conn = await get_async_connection()
        
        async with conn.cursor() as cursor:
            # 1. Verificar si existe la vista
            await cursor.execute("SELECT id FROM modulos_vistas WHERE id = %s", (id_vista,))
            if not await cursor.fetchone():
                return {
                    "success": 0,
                    "message": f"No se encontró la vista con ID {id_vista}",
                    "data": []
                }

            # 2. Consulta principal con la estructura correcta
            query = """
                SELECT 
                    pe.id,
                    pe.modulo AS id_modulo,
                    pe.vista AS id_vista,
                    pe.elemento,
                    mv.nombre_vista,
                    m.modulo AS nombre_modulo
                FROM permisos_elementos pe
                LEFT JOIN modulos_vistas mv ON pe.vista = mv.id
                LEFT JOIN modulos m ON pe.modulo = m.id
                WHERE pe.vista = %s
                ORDER BY pe.id
            """
            await cursor.execute(query, (id_vista,))
            result = await cursor.fetchall()

            if result:
                columns = [desc[0] for desc in cursor.description]
                data = [dict(zip(columns, row)) for row in result]
                
                logging.info(f"Se encontraron {len(data)} elementos para la vista {id_vista}")
                
                return {
                    "success": 1, 
                    "message": f"Se encontraron {len(data)} elementos", 
                    "data": data
                }
            else:
                return {
                    "success": 1,
                    "message": "No hay elementos registrados para esta vista",
                    "data": []
                }

    except Exception as e:
        error_msg = f"Error al consultar elementos para la vista {id_vista}: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return {
            "success": 0,
            "message": error_msg,
            "data": []
        }
    finally:
        if conn:
            await conn.ensure_closed()


async def insertarPermiso(data: dict):
    conn = None
    try:
        conn = await get_async_connection()
        
        id_perfil = data.get("id_perfil")
        id_modulo = data.get("id_modulo")
        id_vista = data.get("id_vista")
        id_elemento = data.get("id_elemento")
        permiso = data.get("permiso")
        
        if id_elemento in [None, '', 'NULL']:
            id_elemento = None
        
        async with conn.cursor() as cursor:
            insert_query = """
                INSERT INTO permisos (id_perfil, id_modulo, id_vista, id_elemento, permiso) 
                VALUES (%s, %s, %s, %s, %s)
            """
            logging.info(f"Datos a insertar: {id_perfil=}, {id_modulo=}, {id_vista=}, {id_elemento=}, {permiso=}")
            await cursor.execute(insert_query, (id_perfil, id_modulo, id_vista, id_elemento, permiso))
            await conn.commit()
            
            id_permiso = cursor.lastrowid
            if not id_permiso:
                await cursor.execute("SELECT LAST_INSERT_ID()")
                row = await cursor.fetchone()
                id_permiso = row[0] if row else None
            
            if not id_permiso:
                return {
                    "success": 0,
                    "message": "No se pudo obtener el ID del permiso insertado",
                    "data": {}
                }
            
            select_query = """
                SELECT p.*, m.modulo, mv.nombre_vista AS vista, pe.elemento 
                FROM permisos p 
                INNER JOIN modulos m ON p.id_modulo = m.id 
                INNER JOIN modulos_vistas mv ON p.id_vista = mv.id 
                LEFT JOIN permisos_elementos pe ON pe.id = p.id_elemento 
                WHERE p.id = %s
            """
            await cursor.execute(select_query, (id_permiso,))
            row = await cursor.fetchone()
            
            if row:
                logging.info(f"Permiso insertado: {row}")
                columns = [col[0] for col in cursor.description]
                permiso_insertado = dict(zip(columns, row))
                return {
                    "success": 1,
                    "message": "Permiso insertado",
                    "data": permiso_insertado
                }
            else:
                return {
                    "success": 0,
                    "message": "Permiso insertado, pero no se pudo recuperar el registro",
                    "data": {}
                }
            
    except Exception as e:
        logging.error(f"Error al insertar permiso: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al insertar permiso: {str(e)}",
            "data": {}
        }
    finally:
        if conn:
            await conn.ensure_closed()

async def actualizarPermiso(id_permiso: int, data: dict):
    conn = None
    try:
        conn = await get_async_connection()
        
        id_perfil = data.get("id_perfil")
        id_modulo = data.get("id_modulo")
        id_vista = data.get("id_vista")
        id_elemento = data.get("id_elemento")
        permiso = data.get("permiso")
        
        async with conn.cursor() as cursor:
            update_query = """
                UPDATE permisos 
                SET id_perfil = %s, id_modulo = %s, id_vista = %s, id_elemento = %s, permiso = %s 
                WHERE id = %s
            """
            await cursor.execute(update_query, (id_perfil, id_modulo, id_vista, id_elemento, permiso, id_permiso))
            await conn.commit()
            
            # Verificar si se actualizó alguna fila
            if cursor.rowcount == 0:
                return {"success": 0, "message": f"No se encontró el permiso con ID {id_permiso}", "data": {}}
            
            select_query = """
                SELECT p.*, m.modulo, mv.nombre_vista AS vista, pe.elemento 
                FROM permisos p 
                INNER JOIN modulos m ON p.id_modulo = m.id 
                INNER JOIN modulos_vistas mv ON p.id_vista = mv.id 
                LEFT JOIN permisos_elementos pe ON pe.id = p.id_elemento 
                WHERE p.id = %s
            """
            await cursor.execute(select_query, (id_permiso,))
            row = await cursor.fetchone()
            
            if row:
                columns = [col[0] for col in cursor.description]
                permiso_actualizado = dict(zip(columns, row))
                return {"success": 1, "message": "Permiso actualizado", "data": permiso_actualizado}
            else:
                return {"success": 0, "message": "Permiso actualizado, pero no se pudo recuperar el registro", "data": {}}
        
    except Exception as e:
        logging.error(f"Error al actualizar permiso: {str(e)}", exc_info=True)
        return {"success": 0, "message": f"Error al actualizar permiso: {str(e)}", "data": {}}
    finally:
        if conn:
            await conn.ensure_closed()


async def eliminarPermiso(id_permiso: int):
    conn = None
    try:
        conn = await get_async_connection()
        async with conn.cursor() as cursor:
            # Verificar si el permiso existe antes de intentar eliminarlo
            check_query = "SELECT id FROM permisos WHERE id = %s"
            await cursor.execute(check_query, (id_permiso,))
            row = await cursor.fetchone()
            
            if not row:
                return {"success": 0, "message": f"No se encontró el permiso con ID {id_permiso}"}
            
            delete_query = "DELETE FROM permisos WHERE id = %s"
            await cursor.execute(delete_query, (id_permiso,))
            await conn.commit()
            
            return {"success": 1, "message": "Permiso eliminado correctamente"}
    
    except Exception as e:
        logging.error(f"Error al eliminar permiso: {str(e)}", exc_info=True)
        return {"success": 0, "message": f"Error al eliminar permiso: {str(e)}"}
    
    finally:
        if conn:
            await conn.ensure_closed()