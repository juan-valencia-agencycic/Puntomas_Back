import mysql.connector
from mysql.connector import Error
from typing import Dict
import sys

sys.path.append('/var/www/html/config')
from cnxpdo import get_connection

def consultarInfoClientes(id_cliente: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT l.ID_CLIENTE, l.NOMBRE, l.APELLIDO, l.STATUS, l.TELEFONO_1, l.AGENTE, l.ESTADOVIVE,
               (SELECT d.full_name FROM usertbl d WHERE l.AGENTE = d.id) as NOMBREAGENTE,
               l.sesion_Credimas
        FROM INFO_CLIENTES l
        WHERE ((ID_CLIENTE = %s) AND (STATUS <> 'Anulado'))
        """
        cursor.execute(query, (id_cliente,))
        rows = cursor.fetchall()

        clientes = []
        for row in rows:
            cliente = {
                "ID_CLIENTE": row[0],
                "NOMBRE": row[1],
                "APELLIDO": row[2],
                "STATUS": row[3],
                "TELEFONO_1": row[4],
                "AGENTE": row[5],
                "ESTADOVIVE": row[6],
                "NOMBREAGENTE": row[7],
                "sesion_Credimas": row[8],
            }
            clientes.append(cliente)

        cursor.close()
        conn.close()

        return {
            "success": True,
            "message": "Clientes encontrados",
            "data": clientes,
        }

    except Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        return {
            "success": False,
            "message": f"Error de conexión a la base de datos: {e}",
        }
    except Exception as e:
        print(f"Error al consultar los clientes: {e}")
        return {
            "success": False,
            "message": f"Error al consultar los clientes: {e}",
        }