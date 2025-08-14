import mysql.connector
from mysql.connector import Error
from typing import Any, Dict, Optional
import sys
from random import randint

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

def obtener_cliente_por_telefono(telefonoCli: str) -> Optional[Dict[str, Any]]:
    """
    Función independiente para obtener datos básicos del cliente a partir de su teléfono.
    Retorna None si no existe cliente activo con ese teléfono.
    """
    con = None
    cursor = None
    try:
        con = get_connection()
        cursor = con.cursor(dictionary=True)
        sql = """
            SELECT a11.ID_CLIENTE as IDCLIENTE, 
                   CONCAT(a11.NOMBRE, ' ', a11.APELLIDO) AS NOMBRECLI, 
                   a11.STATUS, 
                   SUBSTRING(a11.SOCIAL, -4) as social
            FROM info_clientes a11 
            WHERE (a11.TELEFONO_1 = %s OR a11.TELEFONO_2 = %s) 
              AND status='Activo'
        """
        cursor.execute(sql, (telefonoCli, telefonoCli))
        return cursor.fetchone()  # Retorna un dict o None
    except Error as e:
        print(f"Error en la consulta de cliente: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()
             
def consultarCuentasEliminadas(telefonoCli: str, indicador: int, social: str) -> Dict[str, Any]:
    """
    Función principal que retorna información de cuentas eliminadas y mensajes de error.
    Usa la función obtener_cliente_por_telefono para obtener el cliente.
    """
    cliente = obtener_cliente_por_telefono(telefonoCli)
    
    # Si no se encuentra el cliente
    if not cliente:
        return {
            "answer": '🧐 No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "answer_clean": 'No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Actualizar Datos", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    # Verificar último 4 dígitos social
    if cliente['social'] != social:
        return {
            "answer": '🧐 Lo siento pero no encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "answer_clean": 'No encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Contactar Asesor", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    # Solo manejar indicador 7 (cuentas eliminadas)
    if indicador == 7:
        try:
            con2 = get_connection()  # Segunda conexión si aplica
            cursor2 = con2.cursor(dictionary=True)
            sql_acc_deleted = """
                SELECT acreedororiginal, fecharesultado, resulta, fecha, buro, tipcuent 
                FROM acces_clientes 
                WHERE resulta='Deleted' AND ID_CLIENTE=%s
            """
            cursor2.execute(sql_acc_deleted, (cliente['IDCLIENTE'],))
            result_deleted = cursor2.fetchall()

            if result_deleted:
                response_message = 'Estas son tus cuentas eliminadas 👇\n\n'
                for row in result_deleted:
                    response_message += f"Bureau ➜ {row['buro']} \n"
                    response_message += f"Cuenta ➜ {row['acreedororiginal']} \n"
                    response_message += f"Fecha de Eliminación: {row['fecharesultado']} \n"
                    response_message += f"Resultado ➜ Deleted ✅ \n\n"
                response_message += "\n¡Recuerda! \nTambién puedes ver estos resultados en nuestra App \n👉 https://app.credimas.us"
            else:
                response_message = '⏰ Aún no tengo cuentas eliminadas para mostrarte, pero no te preocupes, las disputas están en curso y dentro del tiempo de respuesta *(45 días hábiles)*.'

            return {
                "answer": response_message,
                "answer_clean": response_message,
                "complements": []
            }

        except Error as e:
            return {"error": f"Error en la consulta de cuentas eliminadas: {str(e)}"}
        finally:
            if cursor2:
                cursor2.close()
            if con2:
                con2.close()

def consultar_puntaje_credito(telefonoCli: str, social: str) -> Dict[str, Any]:
    """
    Función que consulta el puntaje de crédito de un cliente. 
    Si no hay puntajes disponibles o si hay algún problema, devuelve un mensaje de error o instrucciones.
    """
    cliente = obtener_cliente_por_telefono(telefonoCli)

    if not cliente:
        return {
            "answer": '🧐 No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "answer_clean": 'No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Actualizar Datos", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    if cliente['social'] != social:
        return {
            "answer": '🧐 Lo siento pero no encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "answer_clean": 'No encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Contactar Asesor", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    # Consulta de puntajes de crédito
    try:
        con2 = get_connection()  # Segunda conexión si aplica
        cursor2 = con2.cursor(dictionary=True)
        sql_score = """
            SELECT puntaje_buros.* 
            FROM puntaje_buros 
            WHERE id_cliente=%s
        """
        cursor2.execute(sql_score, (cliente['IDCLIENTE'],))
        result_scores = cursor2.fetchall()

        if not result_scores:
            msgAux = "🔔 En este momento no tenemos disponible un puntaje de crédito para mostrarte, esto puede deberse a:\n\n"
            msgAux += "▶️ Tu documento de identidad es un ITIN NUMBER\n"
            msgAux += "▶️ Posiblemente puedes tener un bloqueo por los diferentes Bureaus de crédito\n"
            msgAux += "▶️ Fuiste víctima de robo de identidad\n"
            msgAux += "Si tienes dudas comunícate con un asesor para conocer más."
            return {
                "answer": msgAux,
                "answer_clean": msgAux,
                "complements": []
            }

        # Si tiene puntajes
        array_ex = []
        array_eq = []
        array_tr = []

        for row in result_scores:
            array_ex.append(row['puntaje_experian'])
            array_eq.append(row['puntaje_equifax'])
            array_tr.append(row['puntaje_transunion'])

        # Si tiene más de un puntaje
        if len(array_ex) > 1:
            msgAux = f"{cliente['NOMBRECLI']}, tu puntaje anterior era:\n"
            msgAux += f"🚥 Experian ➜ {array_ex[-2]}\n"
            msgAux += f"🚥 Equifax ➜ {array_eq[-2]}\n"
            msgAux += f"🚥 Transunion ➜ {array_tr[-2]}\n"

            if int(array_ex[-1]) > int(array_ex[-2]):
                msgAux += "\nFelicitaciones 🎉🎉\n"
            else:
                msgAux += "\n¡Ahora tu puntaje cambió!\n"

            msgAux += f"tu puntaje de crédito actual es 👇\n"
            msgAux += f"🚥 Experian ➜ {array_ex[-1]}\n"
            msgAux += f"🚥 Equifax ➜ {array_eq[-1]}\n"
            msgAux += f"🚥 Transunion ➜ {array_tr[-1]}\n"
            msgAux += "*Este puntaje se obtiene de las plataformas Identity®️ IQ & Privacy Guard®️.*"
            msgAux += "\n\n+Credimás, más calidad de vida."

        else:
            msgAux = f"{cliente['NOMBRECLI']}, estamos trabajando para que, en la próxima ocasión podamos hacer el comparativo de los puntajes de crédito."
            msgAux += "\nTu puntaje de crédito actual es 👇\n"
            msgAux += f"🚥 Experian ➜ {array_ex[0]}\n"
            msgAux += f"🚥 Equifax ➜ {array_eq[0]}\n"
            msgAux += f"🚥 Transunion ➜ {array_tr[0]}\n"
            msgAux += "*Este puntaje se obtiene de las plataformas Identity®️ IQ & Privacy Guard®️.*"
            msgAux += "\n\n+Credimás, más calidad de vida."

        return {
            "answer": msgAux,
            "answer_clean": msgAux,
            "complements": []
        }

    except Error as e:
        return {"error": f"Error al obtener el puntaje de crédito: {str(e)}"}
    finally:
        if cursor2:
            cursor2.close()
        if con2:
            con2.close()

def consultar_disputas(telefonoCli: str, social: str) -> Dict[str, Any]:
    """
    Función para consultar las disputas físicas y virtuales de un cliente.
    """
    cliente = obtener_cliente_por_telefono(telefonoCli)

    if not cliente:
        return {
            "answer": '🧐 No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "answer_clean": 'No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Actualizar Datos", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    if cliente['social'] != social:
        return {
            "answer": '🧐 Lo siento pero no encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "answer_clean": 'No encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Contactar Asesor", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    # Consultar disputas físicas
    try:
        con2 = get_connection()  # Segunda conexión si aplica
        cursor2 = con2.cursor(dictionary=True)
        
        # Consultar disputas físicas
        sql_fisicas = """
            SELECT * 
            FROM cartas_generadas 
            WHERE id_cliente = %s 
              AND estado = 0 
              AND fecha_creacion BETWEEN DATE_ADD(CURRENT_DATE, INTERVAL -3 MONTH) AND CURDATE()
        """
        cursor2.execute(sql_fisicas, (cliente['IDCLIENTE'],))
        disputas_fisicas = cursor2.fetchall()

        result_disputas = "📑 Disputas Físicas: \n"
        if disputas_fisicas:
            for disputa in disputas_fisicas:
                result_disputas += f"📨 Fecha de Envío: {disputa['fecha_creacion']} \n"
                result_disputas += "Cuentas disputadas: \n"
                
                # Consultar detalles de las disputas
                sql_acc_disputa = """
                    SELECT nombrecuenta, acreedororiginal, statu, fecha, buro 
                    FROM acces_clientes 
                    WHERE ID_ACCES = %s AND ID_CLIENTE = %s
                """
                cursor2.execute(sql_acc_disputa, (disputa['id_acces'], cliente['IDCLIENTE']))
                acces_disputa = cursor2.fetchall()

                for acc in acces_disputa:
                    result_disputas += f"{acc['nombrecuenta']} \n"
                    result_disputas += f"Acreedor: {acc['acreedororiginal']} \n"
                    result_disputas += f"Status: {acc['statu']} \n"
                    result_disputas += f"Buro: {acc['buro']} \n"
        else:
            result_disputas = "No hay disputas físicas en proceso."

        # Consultar disputas virtuales
        sql_virtuales = """
            SELECT * 
            FROM disputa_virtual 
            WHERE id_cliente = %s AND estado = 0 
            ORDER BY id_disputavirt DESC LIMIT 20
        """
        cursor2.execute(sql_virtuales, (cliente['IDCLIENTE'],))
        disputas_virtuales = cursor2.fetchall()

        result_virtuales = "\n📧 Disputas Virtuales: \n"
        if disputas_virtuales:
            for disputa in disputas_virtuales:
                result_virtuales += f"📨 Fecha de Envío: {disputa['fecha_envio']} \n"
                result_virtuales += "Cuentas disputadas: \n"

                # Consultar detalles de las disputas virtuales
                sql_acc_virtual = """
                    SELECT nombrecuenta, acreedororiginal, statu, fecha, buro 
                    FROM acces_clientes 
                    WHERE ID_ACCES = %s AND ID_CLIENTE = %s
                """
                cursor2.execute(sql_acc_virtual, (disputa['ids_access'], cliente['IDCLIENTE']))
                acces_virtual = cursor2.fetchall()

                for acc in acces_virtual:
                    result_virtuales += f"{acc['nombrecuenta']} \n"
                    result_virtuales += f"Acreedor: {acc['acreedororiginal']} \n"
                    result_virtuales += f"Status: {acc['statu']} \n"
                    result_virtuales += f"Buro: {acc['buro']} \n"
        else:
            result_virtuales = "No hay disputas virtuales en proceso."

        # Combinar resultados
        final_result = result_disputas + result_virtuales
        return {
            "answer": final_result,
            "answer_clean": final_result,
            "complements": []
        }

    except Error as e:
        return {"error": f"Error al consultar las disputas: {str(e)}"}
    finally:
        if cursor2:
            cursor2.close()
        if con2:
            con2.close()
            
def consultar_tarjetas_aseguradas(telefonoCli: str, social: str) -> Dict[str, Any]:
    """
    Función para consultar las tarjetas aseguradas asociadas al cliente.
    """
    cliente = obtener_cliente_por_telefono(telefonoCli)

    if not cliente:
        return {
            "answer": '🧐 No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "answer_clean": 'No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Actualizar Datos", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    if cliente['social'] != social:
        return {
            "answer": '🧐 Lo siento pero no encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "answer_clean": 'No encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Contactar Asesor", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    try:
        con2 = get_connection()  # Segunda conexión si aplica
        cursor2 = con2.cursor(dictionary=True)
        
        # Consultar las tarjetas aseguradas
        sql_tarjetas = """
            SELECT a11.ID_CLIENTE, CONCAT(a11.NOMBRE, ' ', a11.APELLIDO) AS NOMBRECLI, a11.STATUS, a12.banco, a12.franquicia, 
                   a12.Estado_tarjeta, a12.Valor_tarjeta as vrtr, a12.varlor_aseguro as vrsg, a12.fecha_limite_pago
            FROM info_clientes a11
            LEFT JOIN tarjeta_prepagada a12 ON (a11.ID_CLIENTE = a12.id_cliente)
            WHERE (a11.TELEFONO_1 = %s OR a11.TELEFONO_2 = %s)
              AND SUBSTRING(a11.SOCIAL, -4) = %s
              AND a12.Estado_tarjeta NOT IN ('Negada','5. Negada')
            ORDER BY a12.id_tarjeta DESC
        """
        cursor2.execute(sql_tarjetas, (telefonoCli, telefonoCli, social))
        tarjetas = cursor2.fetchall()

        if tarjetas:
            arrayDatos2 = f"{cliente['NOMBRECLI']}, A continuación encontrarás las tarjetas aplicadas por nuestro departamento de BackOffice.\n\n"
            for tarjeta in tarjetas:
                estado_tr = tarjeta['Estado_tarjeta']
                if estado_tr == 'Aprobada - Pendiente por asegurar':
                    estado_tr = f'❗️ Pendiente asegurar $ {int(tarjeta["vrsg"])} Hasta: {tarjeta["fecha_limite_pago"]}'
                else:
                    estado_tr = f'✅ {estado_tr}'

                arrayDatos2 += f'🏛️ {tarjeta["banco"]}\n'
                arrayDatos2 += f'💳 {tarjeta["franquicia"]} 💰 Límite $ {int(tarjeta["vrtr"])}\n'
                arrayDatos2 += f'{estado_tr}.\n\n'

            arrayDatos2 += "\n\n+ CREDIMÁS, más calidad de vida."

            return {
                "answer": arrayDatos2,
                "answer_clean": arrayDatos2,
                "complements": []
            }
        else:
            return {
                "answer": 'No encontramos tarjetas asociadas al perfil del cliente.',
                "answer_clean": 'No encontramos tarjetas asociadas al perfil del cliente.',
                "complements": []
            }

    except Error as e:
        return {"error": f"Error al consultar las tarjetas aseguradas: {str(e)}"}
    finally:
        if cursor2:
            cursor2.close()
        if con2:
            con2.close()

def consultar_fecha_pago(telefonoCli: str, social: str) -> Dict[str, Any]:
    """
    Función para consultar la fecha de pago de las tarjetas asociadas al cliente.
    """
    cliente = obtener_cliente_por_telefono(telefonoCli)

    if not cliente:
        return {
            "answer": '🧐 No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "answer_clean": 'No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Actualizar Datos", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    if cliente['social'] != social:
        return {
            "answer": '🧐 Lo siento pero no encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "answer_clean": 'No encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Contactar Asesor", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    try:
        con2 = get_connection()  # Segunda conexión si aplica
        cursor2 = con2.cursor(dictionary=True)
        
        # Consultar la próxima fecha de pago
        sql_pago = """
            SELECT a11.ID_CLIENTE, CONCAT(a11.NOMBRE, ' ', a11.APELLIDO) AS NOMBRECLI, a11.STATUS, a12.numero_tarjeta, 
                   a12.fecha_expedicion_tarjeta, a12.valor_debitar, a12.fecha_debito, a12.numero_pago, a12.estado_pago
            FROM info_clientes a11
            LEFT JOIN procesar_tarjetas a12 ON (a11.ID_CLIENTE = a12.id_cliente)
            WHERE (a11.TELEFONO_1 = %s OR a11.TELEFONO_2 = %s)
              AND SUBSTRING(a11.SOCIAL, -4) = %s
            ORDER BY a12.id_pago DESC
        """
        cursor2.execute(sql_pago, (telefonoCli, telefonoCli, social))
        pagos = cursor2.fetchall()

        if len(pagos) > 1:
            return {
                "answer": '📱 ¡Hola! Hemos detectado que tu número de teléfono aparece más de una vez en nuestro sistema. Para evitar confusiones y asegurar un servicio eficiente, por favor comunícate con nuestra línea de atención para unificar tus datos. ¡Gracias por tu colaboración!',
                "answer_clean": '¡Hola! Hemos detectado que tu número de teléfono aparece más de una vez en nuestro sistema. Para evitar confusiones y asegurar un servicio eficiente, por favor comunícate con nuestra línea de atención para unificar tus datos. ¡Gracias por tu colaboración!',
                "complements": [{"action": "buttons", "param": {"data": [{"label": "Contactar Asesor", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
            }
        elif len(pagos) == 1:
            pago = pagos[0]
            return {
                "answer": f"{pago['NOMBRECLI']}, su próximo pago está programado para el {pago['fecha_debito']}, la cual está asociada a la tarjeta: ************{pago['numero_tarjeta'][-4:]}\n\n+ CREDIMÁS, más calidad de vida.",
                "answer_clean": f"{pago['NOMBRECLI']}, su próximo pago está programado para el {pago['fecha_debito']}, la cual está asociada a la tarjeta: ************{pago['numero_tarjeta'][-4:]}\n\n+ CREDIMÁS, más calidad de vida.",
                "complements": []
            }
        else:
            return {
                "answer": 'No encontramos información del cliente.',
                "answer_clean": 'No encontramos información del cliente.',
                "complements": []
            }

    except Error as e:
        return {"error": f"Error al consultar la fecha de pago: {str(e)}"}
    finally:
        if cursor2:
            cursor2.close()
        if con2:
            con2.close()

def consultar_info_credito(telefonoCli: str, social: str) -> Dict[str, Any]:
    """
    Función para consultar las disputas, puntajes y aplicaciones de crédito asociadas al cliente.
    """
    cliente = obtener_cliente_por_telefono(telefonoCli)

    if not cliente:
        return {
            "answer": '🧐 No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "answer_clean": 'No reconocemos el número desde el que estás consultando. Por favor comunícate con nuestra línea de atención y actualiza tus datos.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Actualizar Datos", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    if cliente['social'] != social:
        return {
            "answer": '🧐 Lo siento pero no encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "answer_clean": 'No encontré información con el código que ingresaste, verifica los últimos 4 números en tu seguro social y vuelve a intentarlo.',
            "complements": [{"action": "buttons", "param": {"data": [{"label": "Contactar Asesor", "type": "message", "value": "Contactar Servicio al Cliente"}]}}]
        }

    try:
        con2 = get_connection()  # Segunda conexión si aplica
        cursor2 = con2.cursor(dictionary=True)

        # Consultar las disputas eliminadas
        sql_disputas = """
            SELECT buro, nombrecuenta, tipcuent, resulta 
            FROM acces_clientes 
            WHERE ID_CLIENTE = %s AND resulta IN ('Deleted') 
            ORDER BY buro
        """
        cursor2.execute(sql_disputas, (cliente['IDCLIENTE'],))
        disputas_eliminadas = cursor2.fetchall()

        result_disputas = "Cuentas eliminadas 👇\n"
        if disputas_eliminadas:
            for disputa in disputas_eliminadas:
                result_disputas += f"📝 {disputa['buro']} ➜ {disputa['nombrecuenta']} | {disputa['tipcuent']} ➜ {disputa['resulta']}\n"
        else:
            result_disputas = "No se encontraron cuentas eliminadas."

        # Consultar las disputas en proceso
        sql_disputas_proceso = """
            SELECT buro, nombrecuenta, tipcuent, resulta 
            FROM acces_clientes 
            WHERE ID_CLIENTE = %s AND resulta IN ('Actualizado', 'En Proceso', 'Verified', 'No response', 'ID req') 
            ORDER BY resulta, buro
        """
        cursor2.execute(sql_disputas_proceso, (cliente['IDCLIENTE'],))
        disputas_proceso = cursor2.fetchall()

        result_disputas += "\nCuentas en Disputa 👇\n"
        if disputas_proceso:
            for disputa in disputas_proceso:
                result_disputas += f"📝 {disputa['buro']} ➜ {disputa['nombrecuenta']} | {disputa['tipcuent']} ➜ {disputa['resulta']}\n"
        else:
            result_disputas += "No se encontraron cuentas en disputa."

        # Consultar puntajes de crédito
        sql_puntajes = """
            SELECT puntaje_experian, puntaje_equifaz, puntaje_transunion 
            FROM info_clientes 
            WHERE ID_CLIENTE = %s
        """
        cursor2.execute(sql_puntajes, (cliente['IDCLIENTE'],))
        puntajes = cursor2.fetchall()

        result_puntajes = "\nPuntajes de Crédito Actual 👇\n"
        if puntajes:
            for puntaje in puntajes:
                result_puntajes += f"🚥 Experian ➜ {puntaje['puntaje_experian']}\n"
                result_puntajes += f"🚥 Equifax ➜ {puntaje['puntaje_equifaz']}\n"
                result_puntajes += f"🚥 Transunion ➜ {puntaje['puntaje_transunion']}\n"
        else:
            result_puntajes += "No se encontraron puntajes de crédito."

        # Consultar aplicaciones de crédito
        sql_credito = """
            SELECT banco, franquicia, Valor_tarjeta, Estado_tarjeta 
            FROM tarjeta_prepagada 
            WHERE Estado_tarjeta <> 'Negada' AND id_cliente = %s
            ORDER BY Estado_tarjeta
        """
        cursor2.execute(sql_credito, (cliente['IDCLIENTE'],))
        creditos_aplicados = cursor2.fetchall()

        result_credito = "\nAplicaciones de Crédito 👇\n"
        if creditos_aplicados:
            for credito in creditos_aplicados:
                estado_tarjeta = credito['Estado_tarjeta']
                result_credito += f"🏛️ {credito['banco']} ➜ 💳 {credito['franquicia']} 💲 {credito['Valor_tarjeta']} ➜ {estado_tarjeta}\n"
        else:
            result_credito += "No se encontraron aplicaciones de crédito."

        final_result = result_disputas + result_puntajes + result_credito

        return {
            "answer": final_result,
            "answer_clean": final_result,
            "complements": []
        }

    except Error as e:
        return {"error": f"Error al consultar la información de crédito: {str(e)}"}
    finally:
        if cursor2:
            cursor2.close()
        if con2:
            con2.close()

def obtener_info_cliente(telefonoCli: str) -> Dict[str, Any]:
    """
    Función para consultar la información personal del cliente basada en su número de teléfono.
    """
    try:
        con = get_connection()
        cursor = con.cursor(dictionary=True)

        # Consultar datos del cliente
        sql = """
            SELECT ID_CLIENTE, SOCIAL, NOMBRE, APELLIDO 
            FROM info_clientes 
            WHERE TELEFONO_1 = %s OR TELEFONO_2 = %s 
            LIMIT 1
        """
        cursor.execute(sql, (telefonoCli, telefonoCli))
        result = cursor.fetchone()

        if result:
            id_cliente = result['ID_CLIENTE']
            social = result['SOCIAL']
            nombre_cli = result['NOMBRE']
            apellido_cli = result['APELLIDO']

            # Obtener los últimos 4 dígitos del número social
            social_aux = social[-4:]

            # Generar números falsos
            num_falso1 = str(randint(999, 9999))
            num_falso2 = str(randint(999, 9999))

            # Generar iterador
            iterador = randint(1, 3)

            # Determinar tipo de documento
            if social[0] == '9':  # Para TAXID
                tipo_doc = "TAXID"
            else:
                tipo_doc = "SSN"

            return {
                'respuesta': 'KO',
                'idCliente': id_cliente,
                'socialCorrecto': social_aux,
                'nombreCli': nombre_cli,
                'apellidoCli': apellido_cli,
                'socialIncorrecto1': num_falso1,
                'socialIncorrecto2': num_falso2,
                'iterador': iterador,
                'tipoDoc': tipo_doc
            }
        else:
            return {
                'respuesta': 'No se encontró información para el teléfono proporcionado.'
            }

    except Error as e:
        return {"error": f"Error al consultar la información del cliente: {str(e)}"}
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()