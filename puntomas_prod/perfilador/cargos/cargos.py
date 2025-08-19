from ftplib import FTP
import asyncmy
import logging
from clases import DatabaseError

logging.basicConfig(level=logging.INFO)


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

async def consultarCargos():
    conn = None
    try:
        # 1. Establecer conexión
        conn = await asyncmy.connect(**DB_CONFIG)
        
        # 2. Ejecutar consulta
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT 
                    ec.id,
                    ec.cargo,
                    ec.descripcion,
                    ec.idArea,
                    ea.area AS nomarea
                FROM empleados_cargos ec
                LEFT JOIN empleados_areas ea ON ea.id = ec.idArea
                ORDER BY ec.id  -- Ordenar por ID u otro campo relevante
            """)
            
            # 3. Convertir resultados a diccionario
            columns = [col[0] for col in cursor.description]
            cargos = [dict(zip(columns, row)) for row in await cursor.fetchall()]
            
            # 4. Validación de datos
            for cargo in cargos:
                if not cargo.get('cargo'):
                    logging.warning(f"Cargo ID {cargo.get('id')} tiene campo 'cargo' vacío")
                
                if cargo.get('descripcion') and len(cargo['descripcion']) > 255:
                    logging.warning(f"Cargo ID {cargo.get('id')} tiene descripción muy larga")
            
            # 5. Retornar resultados
            return {
                "success": 1,
                "message": "Cargos encontrados" if cargos else "No hay cargos registrados",
                "data": cargos,
            }
            
    except Exception as e:
        logging.error(f"Error en consultarCargos: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al consultar cargos: {str(e)}",
            "data": []
        }
    finally:
        if conn:
            await conn.ensure_closed()
    
async def consultarCargosByAreas(idArea: int):
    conn = None
    try:
        # 1. Establecer conexión
        conn = await asyncmy.connect(**DB_CONFIG)
        
        # 2. Primero verificar si el área existe
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT id FROM empleados_areas WHERE id = %s", (idArea,))
            if not await cursor.fetchone():
                return {
                    "success": 0,
                    "message": "Área no encontrada",
                    "data": []
                }
            
            # 3. Si el área existe, consultar sus cargos
            await cursor.execute("""
                SELECT 
                    ec.id,
                    ec.cargo,
                    ec.descripcion,
                    ec.idArea,
                    ea.area AS nomarea,
                    CHAR_LENGTH(ec.cargo) AS cargo_length,
                    CHAR_LENGTH(ec.descripcion) AS descripcion_length
                FROM empleados_cargos ec
                LEFT JOIN empleados_areas ea ON ea.id = ec.idArea
                WHERE ec.idArea = %s
            """, (idArea,))
            
            # 4. Convertir resultados a diccionario
            columns = [col[0] for col in cursor.description]
            cargos = [dict(zip(columns, row)) for row in await cursor.fetchall()]
            
            # 5. Validación de datos
            for cargo in cargos:
                if not cargo.get('cargo'):
                    logging.warning(f"Cargo ID {cargo.get('id')} en área {idArea} tiene campo vacío")
                if cargo.get('descripcion') and len(cargo['descripcion']) > 255:
                    logging.warning(f"Cargo ID {cargo.get('id')} en área {idArea} tiene descripción larga")
            
            # 6. Retornar resultados
            return {
                "success": 1,
                "message": "Cargos encontrados" if cargos else "No hay cargos en esta área",
                "data": cargos,
            }
            
    except Exception as e:
        logging.error(f"Error al consultar cargos por área {idArea}: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al consultar cargos: {str(e)}",
            "data": []
        }
    finally:
        if conn:
            await conn.ensure_closed()

async def insertarCargo(data: dict):
    conn = None
    try:
        conn = await asyncmy.connect(**DB_CONFIG)
        
        async with conn.cursor() as cursor:
            # 1. Verificar si el área existe
            await cursor.execute("SELECT 1 FROM empleados_areas WHERE id = %s", (data["idArea"],))
            if not await cursor.fetchone():
                return {
                    "success": 0,
                    "message": "El área especificada no existe",
                    "data": None
                }

            # 2. Insertar nuevo cargo
            await cursor.execute(
                "INSERT INTO empleados_cargos (cargo, descripcion, idArea) VALUES (%s, %s, %s)",
                (data["cargo"], data["descripcion"], data["idArea"])
            )
            await conn.commit()

            # 3. Obtener datos completos del nuevo cargo
            await cursor.execute("""
                SELECT ec.*, ea.area AS nomarea 
                FROM empleados_cargos ec
                LEFT JOIN empleados_areas ea ON ea.id = ec.idArea
                WHERE ec.id = LAST_INSERT_ID()
            """)
            
            columns = [col[0] for col in cursor.description]
            nuevo_cargo = dict(zip(columns, await cursor.fetchone()))

            return {
                "success": 1,
                "message": "Cargo creado exitosamente",
                "data": nuevo_cargo
            }

    except Exception as e:
        logging.error(f"Error en insertarCargo: {str(e)}", exc_info=True)
        return {
            "success": 0,
            "message": f"Error al crear cargo: {str(e)}",
            "data": None
        }
    finally:
        if conn:
            await conn.ensure_closed()

async def actualizarCargo(id_cargo: int, data: dict):
    conn = None
    try:
        # 1. Establecer conexión
        conn = await asyncmy.connect(**DB_CONFIG)
        
        # 2. Obtener datos del request
        cargo = data.get('cargo')
        descripcion = data.get('descripcion')
        idArea = data.get('idArea')
        
        # 3. Validación básica
        if not cargo:
            return {
                "success": 0,
                "message": "El campo 'cargo' es requerido",
                "data": None
            }
        
        # 4. Ejecutar actualización
        async with conn.cursor() as cursor:
            # Actualizar el cargo
            await cursor.execute("""
                UPDATE empleados_cargos
                SET cargo = %s, descripcion = %s, idArea = %s
                WHERE id = %s
            """, (cargo, descripcion, idArea, id_cargo))
            
            # Verificar si se actualizó algún registro
            if cursor.rowcount == 0:
                return {
                    "success": 0,
                    "message": "No se encontró el cargo con el ID proporcionado",
                    "data": None
                }
            
            # Obtener los datos actualizados con el nombre del área
            await cursor.execute("""
                SELECT 
                    ec.id,
                    ec.cargo,
                    ec.descripcion,
                    ec.idArea,
                    ea.area AS nomarea
                FROM empleados_cargos ec
                LEFT JOIN empleados_areas ea ON ea.id = ec.idArea
                WHERE ec.id = %s
            """, (id_cargo,))
            
            # Convertir resultado a diccionario
            columns = [col[0] for col in cursor.description]
            row = await cursor.fetchone()
            cargo_actualizado = dict(zip(columns, row))
            
            await conn.commit()
            
            return {
                "success": 1,
                "message": "Cargo actualizado exitosamente",
                "data": cargo_actualizado
            }
            
    except Exception as e:
        logging.error(f"Error en actualizarCargo: {str(e)}", exc_info=True)
        if conn:
            await conn.rollback()
        return {
            "success": 0,
            "message": f"Error al actualizar cargo: {str(e)}",
            "data": None
        }
    finally:
        if conn:
            await conn.ensure_closed()

async def eliminarCargo(cargo: int):
    conn = None
    try:
        # 1. Establecer conexión
        conn = await asyncmy.connect(**DB_CONFIG)
        
        # 2. Verificar si el cargo tiene empleados asociados
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT COUNT(*) as count
                FROM empleados_cargos
                WHERE cargo = %s
            """, (cargo,))
            
            # count = (await cursor.fetchone())[0]
            
            # if count > 0:
            #     return {
            #         "success": 0,
            #         "message": "No se puede eliminar el cargo porque tiene empleados asociados",
            #         "data": None
            #     }
            
            # 3. Eliminar el cargo
            await cursor.execute("""
                DELETE FROM empleados_cargos
                WHERE id = %s
            """, (cargo,))
            
            # 4. Verificar si se eliminó algún registro
            if cursor.rowcount == 0:
                return {
                    "success": 0,
                    "message": "No se encontró el cargo con el ID proporcionado",
                    "data": None
                }
            
            await conn.commit()
            
            return {
                "success": 1,
                "message": "Cargo eliminado correctamente",
                "data": {"cargo": cargo}
            }
            
    except Exception as e:
        logging.error(f"Error en eliminarCargo: {str(e)}", exc_info=True)
        if conn:
            await conn.rollback()
        return {
            "success": 0,
            "message": f"Error al eliminar cargo: {str(e)}",
            "data": None
        }
    finally:
        if conn:
            await conn.ensure_closed()