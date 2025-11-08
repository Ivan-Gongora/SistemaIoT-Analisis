import pymysql
import time
from app.servicios.servicio_simulacion import get_db_connection

async def ejecutar_agregacion_horaria():
    """
    Lee la tabla 'valores' de la última hora, calcula los agregados
    (AVG o SUM según el tipo de campo) y los inserta o actualiza 
    en 'valores_agregados'.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ejecutando agregación horaria inteligente...")

            # 🚨 CONSULTA SQL ACTUALIZADA (CON LÓGICA CONDICIONAL) 🚨
            sql_aggregate = """
            INSERT INTO valores_agregados 
                (campo_id, fecha, hora, valor_min, valor_max, valor_avg, valor_sum, total_registros)
            SELECT
                v.campo_id,
                DATE(v.fecha_hora_lectura) AS fecha,
                HOUR(v.fecha_hora_lectura) AS hora,
                
                -- Min y Max se calculan para todos
                MIN(v.valor) AS valor_min,
                MAX(v.valor) AS valor_max,
                
                -- Lógica Condicional para AVG:
                -- Si el nombre del campo es 'Movimiento', AVG es NULL.
                CASE 
                    WHEN cs.nombre = 'Movimiento' THEN NULL
                    ELSE AVG(v.valor)
                END AS valor_avg,
                
                -- Lógica Condicional para SUM:
                -- Si el nombre es 'Movimiento', calculamos SUM().
                CASE
                    WHEN cs.nombre = 'Movimiento' THEN SUM(v.valor)
                    ELSE NULL
                END AS valor_sum,
                
                COUNT(*) AS total_registros
            FROM
                valores v
            -- 🚨 Unimos con campos_sensores para saber el nombre del campo
            JOIN 
                campos_sensores cs ON v.campo_id = cs.id
            WHERE
                -- Procesa solo los datos de las últimas 2 horas (margen de seguridad)
                v.fecha_hora_lectura >= NOW() - INTERVAL 2 HOUR
            GROUP BY
                v.campo_id, cs.nombre, fecha, hora
            
            -- Actualiza los campos correspondientes
            ON DUPLICATE KEY UPDATE
                valor_min = VALUES(valor_min),
                valor_max = VALUES(valor_max),
                valor_avg = VALUES(valor_avg),       -- Actualiza AVG (será NULL para Movimiento)
                valor_sum = VALUES(valor_sum),       -- Actualiza SUM (será NULL para otros)
                total_registros = valores_agregados.total_registros + VALUES(total_registros);
            """
            
            affected_rows = cursor.execute(sql_aggregate)
            conn.commit()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Agregación completada. Filas afectadas/actualizadas: {affected_rows}")

    except Exception as e:
        print(f"Error en agregación programada: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()



# import pymysql
# import time
# from app.servicios.servicio_simulacion import get_db_connection

# async def ejecutar_agregacion_horaria():
#     """
#     Lee la tabla 'valores' de la última hora, calcula los agregados
#     y los inserta o actualiza en 'valores_agregados'.
#     """
#     conn = None
#     try:
#         conn = get_db_connection()
#         with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            
#             print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ejecutando agregación horaria...")

#             # 🚨 ESTA ES LA CONSULTA SQL OPTIMIZADA PARA PRODUCCIÓN 🚨
#             # Inserta nuevos resúmenes o actualiza los existentes si ya hay datos para esa hora.
#             sql_aggregate = """
#             INSERT INTO valores_agregados 
#                 (campo_id, fecha, hora, valor_min, valor_max, valor_avg, total_registros)
#             SELECT
#                 campo_id,
#                 DATE(fecha_hora_lectura) AS fecha,
#                 HOUR(fecha_hora_lectura) AS hora,
#                 MIN(valor) AS valor_min,
#                 MAX(valor) AS valor_max,
#                 AVG(valor) AS valor_avg,
#                 COUNT(*) AS total_registros
#             FROM
#                 valores
#             WHERE
#                 -- Procesa solo los datos de las últimas 2 horas (margen de seguridad)
#                 fecha_hora_lectura >= NOW() - INTERVAL 2 HOUR
#             GROUP BY
#                 campo_id, fecha, hora
#             ON DUPLICATE KEY UPDATE
#                 -- Si ya existe un resumen para esa hora, lo actualiza
#                 valor_min = LEAST(valores_agregados.valor_min, VALUES(valor_min)),
#                 valor_max = GREATEST(valores_agregados.valor_max, VALUES(valor_max)),
#                 valor_avg = ( (valores_agregados.valor_avg * valores_agregados.total_registros) + (VALUES(valor_avg) * VALUES(total_registros)) ) 
#                             / (valores_agregados.total_registros + VALUES(total_registros)),
#                 total_registros = valores_agregados.total_registros + VALUES(total_registros);
#             """
            
#             affected_rows = cursor.execute(sql_aggregate)
#             conn.commit()
#             print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Agregación completada. Filas afectadas/actualizadas: {affected_rows}")

#     except Exception as e:
#         print(f"Error en agregación programada: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if conn:
#             conn.close()