# # app/api/rutas/valores/valores.py
# app/api/rutas/valores/valores.py

from fastapi import Path, Body
from fastapi import APIRouter, Query, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pymysql

from app.servicios.auth_utils import get_current_user_id
from app.configuracion import configuracion
from app.servicios.servicio_simulacion import get_db_connection
from app.api.modelos.valores import Valor 

router = APIRouter()

@router.get("/valores/historico-campo/{campo_id}", response_model=List[Valor])
async def get_valores_historicos(
    campo_id: int,
    fecha_inicio: Optional[datetime] = Query(None, description="Filtro de fecha inicial (ISO 8601)"),
    fecha_fin: Optional[datetime] = Query(None, description="Filtro de fecha final (ISO 8601)"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Obtiene los registros históricos de un campo de sensor específico.
    OPTIMIZADO: Usa 'valores_agregados' para rangos largos.
    """
    try:
        if not fecha_fin:
            fecha_fin = datetime.now()
        if not fecha_inicio:
            fecha_inicio = fecha_fin - timedelta(days=7) 

        valores = await obtener_valores_por_campo_db(campo_id, fecha_inicio, fecha_fin)
        
        if not valores:
            return []
        
        return valores
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener valores: {str(e)}")


# ----------------------------------------------------------------------
# ENDPOINT (INTELIGENTE) DE DATOS HISTÓRICOS (Existente)
# ----------------------------------------------------------------------
# @router.get("/valores/historico-campo/{campo_id}", response_model=List[Valor])
# async def get_valores_historicos(
#     campo_id: int,
#     fecha_inicio: Optional[datetime] = Query(None, description="Filtro de fecha inicial (ISO 8601)"),
#     fecha_fin: Optional[datetime] = Query(None, description="Filtro de fecha final (ISO 8601)"),
#     current_user_id: int = Depends(get_current_user_id)
# ):
#     """
#     Obtiene los registros históricos de un campo de sensor específico.
#     OPTIMIZADO: Usa 'valores_agregados' para rangos largos.
#     """
#     try:
#         if not fecha_fin:
#             fecha_fin = datetime.now()
#         if not fecha_inicio:
#             fecha_inicio = fecha_fin - timedelta(days=7) 

#         valores = await obtener_valores_por_campo_db(campo_id, fecha_inicio, fecha_fin)
        
#         if not valores:
#             return []
        
#         return valores
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error al obtener valores: {str(e)}")

# ----------------------------------------------------------------------
# 🚨 ENDPOINT NUEVO: Obtener rango de fechas (MIN/MAX)
# ----------------------------------------------------------------------
@router.get("/valores/rango-fechas-dispositivo/{dispositivo_id}")
async def get_rango_fechas_dispositivo(
    dispositivo_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Obtiene la fecha del primer y último registro agregado
    para todos los campos de un dispositivo.
    Consulta la tabla 'valores_agregados' para máxima velocidad.
    """
    try:
        rango = await obtener_rango_fechas_db(dispositivo_id)
        if not rango or not rango.get("fecha_minima"):
             raise HTTPException(status_code=404, detail="No se encontraron datos históricos para este dispositivo.")
        return rango
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener rango de fechas: {str(e)}")


# ----------------------------------------------------------------------
# FUNCIÓN DE SERVICIO DE BASE DE DATOS (Optimizada)
# ----------------------------------------------------------------------

# async def obtener_valores_por_campo_db(
#     campo_id: int, 
#     fecha_inicio: datetime,
#     fecha_fin: datetime
# ) -> List[Dict[str, Any]]:
    
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
        
#         rango_en_dias = (fecha_fin - fecha_inicio).days
        
#         # 1. RANGO CORTO (ej. 2 días o menos): Consultar datos crudos
#         if rango_en_dias <= 2:
#             print(f"--- CONSULTA RANGO CORTO (RAW): {rango_en_dias} días ---")
#             sql = """
#             SELECT
#                 v.id, v.valor, v.fecha_hora_lectura, v.fecha_hora_registro, v.campo_id,
#                 um.magnitud_tipo  
#             FROM valores v
#             JOIN campos_sensores cs ON v.campo_id = cs.id
#             LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
#             WHERE
#                 v.campo_id = %s
#                 AND v.fecha_hora_lectura BETWEEN %s AND %s
#             ORDER BY v.fecha_hora_lectura ASC;
#             """
#             params = [campo_id, fecha_inicio, fecha_fin]

#         # 2. RANGO LARGO (más de 2 días): Consultar datos agregados
#         else:
#             print(f"--- CONSULTA RANGO LARGO (AGREGADA): {rango_en_dias} días ---")
#             sql = """
#             SELECT
#                 va.id, 
#                 va.valor_avg AS valor,
#                 TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_lectura,
#                 TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_registro,
#                 va.campo_id,
#                 um.magnitud_tipo
#             FROM 
#                 valores_agregados va
#             JOIN 
#                 campos_sensores cs ON va.campo_id = cs.id
#             LEFT JOIN 
#                 unidades_medida um ON cs.unidad_medida_id = um.id
#             WHERE 
#                 va.campo_id = %s
#                 AND va.fecha BETWEEN %s AND %s
#             ORDER BY va.fecha, va.hora ASC;
#             """
#             params = [campo_id, fecha_inicio.date(), fecha_fin.date()]
        
#         cursor.execute(sql, params)
#         return cursor.fetchall()
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"DB Error al obtener valores: {str(e)}")
#     finally:
#         if conn: conn.close()

# ----------------------------------------------------------------------
# 🚨 FUNCIÓN DE SERVICIO NUEVA: Para el rango de fechas
# ----------------------------------------------------------------------
async def obtener_rango_fechas_db(dispositivo_id: int) -> Dict[str, Any]:
    """
    Consulta 'valores_agregados' (la tabla rápida) para encontrar 
    el MIN(fecha) y MAX(fecha) para un dispositivo_id dado.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Esta consulta une la tabla agregada con los sensores
        sql = """
        SELECT 
            MIN(va.fecha) AS fecha_minima,
            MAX(va.fecha) AS fecha_maxima
        FROM valores_agregados va
        JOIN campos_sensores cs ON va.campo_id = cs.id
        JOIN sensores s ON cs.sensor_id = s.id
        WHERE s.dispositivo_id = %s;
        """
        
        cursor.execute(sql, (dispositivo_id,))
        return cursor.fetchone() # Devuelve -> {"fecha_minima": "...", "fecha_maxima": "..."}
        
    except Exception as e:
        print(f"Error en DB (obtener_rango_fechas_db): {e}")
        raise e
    finally:
        if conn: conn.close()

# # app/api/rutas/valores/valores.py
# # 🚨 VERSIÓN FINAL (OPTIMIZACIÓN ACTIVADA)

# from fastapi import Path, Body
# from fastapi import APIRouter, Query, HTTPException, Depends, status
# from fastapi.responses import JSONResponse
# from typing import Optional, List, Dict, Any
# from datetime import datetime, timedelta
# import pymysql

# from app.servicios.auth_utils import get_current_user_id
# from app.configuracion import configuracion
# from app.servicios.servicio_simulacion import get_db_connection
# from app.api.modelos.valores import Valor

# router = APIRouter()

# # ----------------------------------------------------------------------
# # ENDPOINT (INTELIGENTE)
# # ----------------------------------------------------------------------
# @router.get("/valores/historico-campo/{campo_id}", response_model=List[Valor])
# async def get_valores_historicos(
#     campo_id: int,
#     fecha_inicio: Optional[datetime] = Query(None, description="Filtro de fecha inicial (ISO 8601)"),
#     fecha_fin: Optional[datetime] = Query(None, description="Filtro de fecha final (ISO 8601)"),
#     current_user_id: int = Depends(get_current_user_id)
# ):
#     """
#     Obtiene los registros históricos de un campo de sensor específico.
#     OPTIMIZADO: Usa 'valores_agregados' para rangos largos.
#     """
#     try:
#         if not fecha_fin:
#             fecha_fin = datetime.now()
#         if not fecha_inicio:
#             fecha_inicio = fecha_fin - timedelta(days=7) 

#         valores = await obtener_valores_por_campo_db(campo_id, fecha_inicio, fecha_fin)
        
#         if not valores:
#             return []
        
#         return valores
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error al obtener valores: {str(e)}")

# # ----------------------------------------------------------------------
# # FUNCIÓN DE SERVICIO DE BASE DE DATOS (LÓGICA 'INTELIGENTE' ACTIVADA)
# # ----------------------------------------------------------------------

async def obtener_valores_por_campo_db(
    campo_id: int, 
    fecha_inicio: datetime,
    fecha_fin: datetime
) -> List[Dict[str, Any]]:
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 🚨 LÓGICA DE OPTIMIZACIÓN 🚨
        rango_en_dias = (fecha_fin - fecha_inicio).days
        
        # 1. RANGO CORTO (ej. 2 días o menos): Consultar datos crudos
        if rango_en_dias <= 2:
            print(f"--- CONSULTA RANGO CORTO (RAW): {rango_en_dias} días ---")
            sql = """
            SELECT
                v.id,
                v.valor,
                v.fecha_hora_lectura,
                v.fecha_hora_registro,
                v.campo_id,
                um.magnitud_tipo  
            FROM
                valores v
            JOIN
                campos_sensores cs ON v.campo_id = cs.id
            LEFT JOIN
                unidades_medida um ON cs.unidad_medida_id = um.id
            WHERE
                v.campo_id = %s
                AND v.fecha_hora_lectura BETWEEN %s AND %s
            ORDER BY v.fecha_hora_lectura ASC;
            """
            params = [campo_id, fecha_inicio, fecha_fin]

        # 2. RANGO LARGO (más de 2 días): Consultar datos agregados
        else:
            # print(f"--- CONSULTA RANGO LARGO (AGREGADA): {rango_en_dias} días ---")
            # sql = """
            # SELECT
            #     va.id, 
            #     va.valor_avg AS valor, -- 👈 Alias AS valor
            #     TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_lectura,
            #     TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_registro,
            #     va.campo_id,
            #     um.magnitud_tipo
            # FROM 
            #     valores_agregados va
            # JOIN 
            #     campos_sensores cs ON va.campo_id = cs.id
            # LEFT JOIN 
            #     unidades_medida um ON cs.unidad_medida_id = um.id
            # WHERE 
            #     va.campo_id = %s
            #     AND va.fecha BETWEEN %s AND %s
            # ORDER BY va.fecha, va.hora ASC;
            # """
            # params = [campo_id, fecha_inicio.date(), fecha_fin.date()]
            print(f"--- CONSULTA RANGO LARGO (AGREGADA): {rango_en_dias} días ---")
            sql = """
            SELECT
                va.id, 
                
                -- 🚨 Lógica Condicional:
                -- Si el nombre es 'Movimiento', devuelve la SUMA,
                -- de lo contrario, devuelve el PROMEDIO.
                CASE
                    WHEN cs.nombre = 'Movimiento' THEN va.valor_sum
                    ELSE va.valor_avg
                END AS valor, -- 👈 Alias AS valor
                
                TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_lectura,
                TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_registro,
                va.campo_id,
                um.magnitud_tipo
            FROM 
                valores_agregados va
            JOIN 
                campos_sensores cs ON va.campo_id = cs.id -- 👈 UNIMOS para saber el nombre
            LEFT JOIN 
                unidades_medida um ON cs.unidad_medida_id = um.id
            WHERE 
                va.campo_id = %s
                AND va.fecha BETWEEN %s AND %s
            ORDER BY va.fecha, va.hora ASC;
            """
            params = [campo_id, fecha_inicio.date(), fecha_fin.date()]
        
        cursor.execute(sql, params)
        return cursor.fetchall()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error al obtener valores: {str(e)}")
    finally:
        if conn: conn.close()

# # app/api/rutas/valores/valores.py
# # 🚨 VERSIÓN DE PRUEBA: Optimizaciones deshabilitadas temporalmente.
# # 🚨 Siempre consultará la tabla 'valores' (datos crudos).

# from fastapi import Path, Body
# from fastapi import APIRouter, Query, HTTPException, Depends, status
# from fastapi.responses import JSONResponse
# from typing import Optional, List, Dict, Any
# from datetime import datetime, timedelta
# import pymysql

# from app.servicios.auth_utils import get_current_user_id
# from app.configuracion import configuracion
# from app.servicios.servicio_simulacion import get_db_connection
# from app.api.modelos.valores import Valor

# router = APIRouter()

# # ----------------------------------------------------------------------
# # ENDPOINT
# # ----------------------------------------------------------------------
# @router.get("/valores/historico-campo/{campo_id}", response_model=List[Valor])
# async def get_valores_historicos(
#     campo_id: int,
#     fecha_inicio: Optional[datetime] = Query(None, description="Filtro de fecha inicial (ISO 8601)"),
#     fecha_fin: Optional[datetime] = Query(None, description="Filtro de fecha final (ISO 8601)"),
#     current_user_id: int = Depends(get_current_user_id)
# ):
#     """
#     Obtiene los registros históricos de un campo de sensor específico,
#     permitiendo filtrar por rango de fechas.
#     (NOTA: Lógica de agregación deshabilitada temporalmente para pruebas).
#     """
#     try:
#         if not fecha_fin:
#             fecha_fin = datetime.now()
#         if not fecha_inicio:
#             fecha_inicio = fecha_fin - timedelta(days=7) 

#         valores = await obtener_valores_por_campo_db(campo_id, fecha_inicio, fecha_fin)
        
#         if not valores:
#             return []
        
#         return valores
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error al obtener valores: {str(e)}")

# # ----------------------------------------------------------------------
# # FUNCIÓN DE SERVICIO DE BASE DE DATOS (LÓGICA 'INTELIGENTE' DESHABILITADA)
# # ----------------------------------------------------------------------

# async def obtener_valores_por_campo_db(
#     campo_id: int, 
#     fecha_inicio: datetime,
#     fecha_fin: datetime
# ) -> List[Dict[str, Any]]:
    
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
        
#         # 🚨 LÓGICA DE OPTIMIZACIÓN DESHABILITADA 🚨
#         # Siempre consultamos la tabla 'valores' (datos crudos)
        
#         rango_en_dias = (fecha_fin - fecha_inicio).days
#         print(f"--- CONSULTA (RAW): {rango_en_dias} días ---")
        
#         sql = """
#         SELECT
#             v.id,
#             v.valor,
#             v.fecha_hora_lectura,
#             v.fecha_hora_registro,
#             v.campo_id,
#             um.magnitud_tipo  
#         FROM
#             valores v
#         JOIN
#             campos_sensores cs ON v.campo_id = cs.id
#         LEFT JOIN
#             unidades_medida um ON cs.unidad_medida_id = um.id
#         WHERE
#             v.campo_id = %s
#             AND v.fecha_hora_lectura BETWEEN %s AND %s
#         ORDER BY v.fecha_hora_lectura ASC;
#         """
#         params = [campo_id, fecha_inicio, fecha_fin]

#         cursor.execute(sql, params)
#         return cursor.fetchall()
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"DB Error al obtener valores: {str(e)}")
#     finally:
#         if conn: conn.close()
# from fastapi import Path, Body
# from fastapi import APIRouter, Query, HTTPException, Depends, status
# from fastapi.responses import JSONResponse
# from typing import Optional, List, Dict, Any
# from datetime import datetime, timedelta # 👈 Importar timedelta
# import pymysql

# from app.servicios.auth_utils import get_current_user_id
# from app.configuracion import configuracion
# from app.servicios.servicio_simulacion import get_db_connection
# from app.api.modelos.valores import Valor # 👈 Modelo Pydantic

# router = APIRouter()

# # ----------------------------------------------------------------------
# # ENDPOINT (Sin cambios, pero ahora es 'inteligente')
# # ----------------------------------------------------------------------
# @router.get("/valores/historico-campo/{campo_id}", response_model=List[Valor])
# async def get_valores_historicos(
#     campo_id: int,
#     fecha_inicio: Optional[datetime] = Query(None, description="Filtro de fecha inicial (ISO 8601)"),
#     fecha_fin: Optional[datetime] = Query(None, description="Filtro de fecha final (ISO 8601)"),
#     current_user_id: int = Depends(get_current_user_id)
# ):
#     """
#     Obtiene los registros históricos de un campo de sensor específico,
#     permitiendo filtrar por rango de fechas.
#     OPTIMIZADO: Usa 'valores_agregados' para rangos largos.
#     """
#     try:
#         # Poner fechas por defecto si no se proveen (ej. últimos 7 días)
#         if not fecha_fin:
#             fecha_fin = datetime.now()
#         if not fecha_inicio:
#             fecha_inicio = fecha_fin - timedelta(days=7) # 👈 Ejemplo: 7 días por defecto

#         valores = await obtener_valores_por_campo_db(campo_id, fecha_inicio, fecha_fin)
        
#         if not valores:
#             return []
        
#         return valores
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error al obtener valores: {str(e)}")

# # ----------------------------------------------------------------------
# # FUNCIÓN DE SERVICIO DE BASE DE DATOS (AQUÍ ESTÁ LA MAGIA)
# # ----------------------------------------------------------------------

# async def obtener_valores_por_campo_db(
#     campo_id: int, 
#     fecha_inicio: datetime, # 👈 Asumimos que las fechas ahora son requeridas
#     fecha_fin: datetime
# ) -> List[Dict[str, Any]]:
    
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
        
#         # 🚨 LÓGICA DE OPTIMIZACIÓN 🚨
#         # Decidimos qué tabla consultar basado en el rango de tiempo
        
#         rango_en_dias = (fecha_fin - fecha_inicio).days
        
#         # 1. RANGO CORTO (ej. 2 días o menos): Consultar datos crudos
#         if rango_en_dias <= 2:
#             print(f"--- CONSULTA RANGO CORTO (RAW): {rango_en_dias} días ---")
#             sql = """
#             SELECT
#                 v.id,
#                 v.valor,
#                 v.fecha_hora_lectura,
#                 v.fecha_hora_registro,
#                 v.campo_id,
#                 um.magnitud_tipo  
#             FROM
#                 valores v
#             JOIN
#                 campos_sensores cs ON v.campo_id = cs.id
#             LEFT JOIN
#                 unidades_medida um ON cs.unidad_medida_id = um.id
#             WHERE
#                 v.campo_id = %s
#                 AND v.fecha_hora_lectura BETWEEN %s AND %s
#             ORDER BY v.fecha_hora_lectura ASC;
#             """
#             params = [campo_id, fecha_inicio, fecha_fin]

#         # 2. RANGO LARGO (más de 2 días): Consultar datos agregados
#         else:
#             print(f"--- CONSULTA RANGO LARGO (AGREGADA): {rango_en_dias} días ---")
#             sql = """
#             SELECT
#                 va.id, 
#                 va.valor_avg AS valor, -- 👈 Alias AS valor
#                 -- Convertimos fecha y hora en un datetime completo
#                 TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_lectura,
#                 -- Usamos el mismo valor para el registro (Pydantic lo requiere)
#                 TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) AS fecha_hora_registro,
#                 va.campo_id,
#                 um.magnitud_tipo
#             FROM 
#                 valores_agregados va
#             JOIN 
#                 campos_sensores cs ON va.campo_id = cs.id
#             LEFT JOIN 
#                 unidades_medida um ON cs.unidad_medida_id = um.id
#             WHERE 
#                 va.campo_id = %s
#                 AND va.fecha BETWEEN %s AND %s
#             ORDER BY va.fecha, va.hora ASC;
#             """
#             params = [campo_id, fecha_inicio.date(), fecha_fin.date()]
        
#         cursor.execute(sql, params)
#         return cursor.fetchall()
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"DB Error al obtener valores: {str(e)}")
#     finally:
#         if conn: conn.close()

# @router.get("/valores/")
# async def obtener_valores(
#     id: Optional[int] = Query(None, description="Identificacion"),
#     campo_id: Optional[int] = Query(None, description="Filtrar por ID del campo"),
#     fecha_inicio: Optional[str] = Query(None, description="Fecha inicial en formato YYYY-MM-DD"),
#     fecha_fin: Optional[str] = Query(None, description="Fecha final en formato YYYY-MM-DD")
# ) -> List[Dict]:
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         query = "SELECT * FROM valores WHERE 1=1"
#         params = []

#         if id is not None:
#             query += " AND id = %s"
#             params.append(id)
#         if campo_id is not None:
#             query += " AND campo_id = %s"
#             params.append(campo_id)
        
#         if fecha_inicio:
#             query += " AND fecha_hora_lectura >= %s"
#             params.append(fecha_inicio)

#         if fecha_fin:
#             query += " AND fecha_hora_lectura <= %s"
#             params.append(fecha_fin)

#         cursor.execute(query, params)
#         resultados = cursor.fetchall()
#         return resultados

#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")
#     finally:
#         conn.close()


# @router.delete("/valores/")
# async def eliminar_valores(
#     id: Optional[int] = Query(None, description="Identificacion"),
#     campo_id: Optional[int] = Query(None, description="Eliminar por campo_id"),
#     fecha_limite: Optional[str] = Query(None, description="Eliminar datos anteriores a esta fecha (YYYY-MM-DD)")
# ) -> Dict:
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         query = "DELETE FROM valores WHERE 1=1"
#         params = []

#         if id is not None:
#             query += " And id = %s"
#             params.append(id)

#         if campo_id is not None:
#             query += " AND campo_id = %s"
#             params.append(campo_id)

#         if fecha_limite:
#             query += " AND fecha_hora_lectura < %s"
#             params.append(fecha_limite)

#         resultado = cursor.execute(query, params)
#         conn.commit()
#         return {"message": f"{resultado} registros eliminados."}

#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Error al eliminar datos: {str(e)}")
#     finally:
#         conn.close()

# @router.post("/valores/")
# async def crear_valor(valor: ValorCrear = Body(...)) -> Dict:
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         query = """
#             INSERT INTO valores (valor, fecha_hora_lectura, campo_id)
#             VALUES (%s, %s, %s)
#         """
#         params = (valor.valor, valor.fecha_hora_lectura, valor.campo_id)

#         cursor.execute(query, params)
#         conn.commit()

#         return {
#             "message": "Valor insertado correctamente",
#             "id_generado": cursor.lastrowid
#         }

#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Error al insertar valor: {str(e)}")
#     finally:
#         conn.close()

# @router.put("/valores/")
# async def actualizar_valor(
#     id: int = Query(..., description="ID del valor a actualizar"),
#     valor: ValorActualizar = Body(...)
# ) -> Dict:
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         campos = []
#         params = []

#         if valor.campo_id is not None:
#             campos.append("campo_id = %s")
#             params.append(valor.campo_id)
#         if valor.valor is not None:
#             campos.append("valor = %s")
#             params.append(valor.valor)
#         if valor.fecha_hora_lectura is not None:
#             campos.append("fecha_hora_lectura = %s")
#             params.append(valor.fecha_hora_lectura)

#         if not campos:
#             raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")

#         query = f"UPDATE valores SET {', '.join(campos)} WHERE id = %s"
#         params.append(id)

#         resultado = cursor.execute(query, params)
#         conn.commit()

#         if resultado == 0:
#             raise HTTPException(status_code=404, detail=f"No se encontró valor con id {id}")

#         return {"message": f"Valor con id {id} actualizado correctamente"}

#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Error al actualizar valor: {str(e)}")
#     finally:
#         conn.close()



# # Simular datos desde json
# @router.post("/simularDatos/")
# async def simular_datos(datos: DatosSimulacionJson):
#     try:
#         print(f"Proyecto: {datos.proyecto}")
#         print(f"Dispositivo: {datos.dispositivo}")
#         print(f"Fecha: {datos.fecha}, Hora: {datos.hora}")
#         print(f"Sensores recibidos: {len(datos.sensores)}")

#         for sensor in datos.sensores:
#             print(f"Sensor: {sensor.nombre}")
#             for campo in sensor.campos_sensores:
#                 print(f"  Campo: {campo.nombre}")
#                 for valor in campo.valores:
#                     print(f"    Datos: {valor.datos}")



#         resultados = await simular_datos_json(datos)
        

#         return {"message": "Simulación completada con JSON.", "resultados": resultados}

#     except ValueError as e:
#         return {"message": "Error en los datos enviados", "details": str(e)}
#     except Exception as e:
#         print("Excepción general:", type(e), e)
#         return JSONResponse(
#             status_code=500,
#             content={"message": "Error inesperado durante la simulación", "details": str(e)},
#         )
# 🚨 RUTA RENOMBRADA a /valores/historico-campo/{campo_id} para evitar conflictos
# @router.get("/valores/historico-campo/{campo_id}", response_model=List[Valor])
# async def get_valores_historicos(
#     campo_id: int,
#     fecha_inicio: Optional[datetime] = Query(None, description="Filtro de fecha inicial (ISO 8601)"),
#     fecha_fin: Optional[datetime] = Query(None, description="Filtro de fecha final (ISO 8601)"),
#     current_user_id: int = Depends(get_current_user_id)
# ):
#     """
#     Obtiene los registros históricos de un campo de sensor específico,
#     permitiendo filtrar por rango de fechas.
#     """
#     try:
#         valores = await obtener_valores_por_campo_db(campo_id, fecha_inicio, fecha_fin)
        
#         # Si no se encuentran valores, devolvemos una lista vacía (200 OK).
#         if not valores:
#             return []
        
#         return valores
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         # En caso de error de DB o cualquier otro, devolvemos 500
#         raise HTTPException(status_code=500, detail=f"Error al obtener valores: {str(e)}")

# # ----------------------------------------------------------------------
# # FUNCIONES DE SERVICIO DE BASE DE DATOS
# # ----------------------------------------------------------------------

# async def obtener_valores_por_campo_db(
#     campo_id: int, 
#     fecha_inicio: Optional[datetime] = None, 
#     fecha_fin: Optional[datetime] = None
# ) -> List[Dict[str, Any]]:
    
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
        
#         # ✅ CONSULTA CORREGIDA: Usando fecha_hora_registro en lugar de fecha_dispositivo
#         sql = """
#         SELECT
#             v.id,
#             v.valor,
#             v.fecha_hora_lectura,
#             v.fecha_hora_registro,  -- ✅ CORREGIDO: fecha_hora_registro existe
#             v.campo_id,
#             um.magnitud_tipo  
#         FROM
#             valores v
#         JOIN
#             campos_sensores cs ON v.campo_id = cs.id
#         LEFT JOIN
#             unidades_medida um ON cs.unidad_medida_id = um.id
#         WHERE
#             v.campo_id = %s
#         """
#         params = [campo_id]
        
#         if fecha_inicio:
#             sql += " AND v.fecha_hora_lectura >= %s"
#             params.append(fecha_inicio)
#         if fecha_fin:
#             sql += " AND v.fecha_hora_lectura <= %s"
#             params.append(fecha_fin)
            
#         sql += " ORDER BY v.fecha_hora_lectura ASC;"
        
#         cursor.execute(sql, params)
#         return cursor.fetchall()
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"DB Error al obtener valores: {str(e)}")
#     finally:
#         if conn: conn.close()


# async def obtener_valores_por_campo_db(
#     campo_id: int, 
#     fecha_inicio: Optional[datetime] = None, 
#     fecha_fin: Optional[datetime] = None
# ) -> List[Dict[str, Any]]:
    
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
        
#         # 🚨 CONSULTA CORREGIDA: Usando el nombre de tabla 'campos_sensores'
#         sql = """
#         SELECT
#             v.id,
#             v.valor,
#             v.fecha_hora_lectura,
#             v.fecha_dispositivo,
#             v.campo_id,
#             um.magnitud_tipo  
#         FROM
#             valores v
#         JOIN
#             campos_sensores cs ON v.campo_id = cs.id  -- 👈 CORRECCIÓN AQUÍ
#         LEFT JOIN
#             unidades_medida um ON cs.unidad_medida_id = um.id -- 👈 Y AQUÍ: usando cs.unidad_medida_id
#         WHERE
#             v.campo_id = %s
#         """
#         params = [campo_id]
        
#         if fecha_inicio:
#             sql += " AND v.fecha_hora_lectura >= %s"
#             params.append(fecha_inicio)
#         if fecha_fin:
#             sql += " AND v.fecha_hora_lectura <= %s"
#             params.append(fecha_fin)
            
#         sql += " ORDER BY v.fecha_hora_lectura ASC;"
        
#         cursor.execute(sql, params)
#         return cursor.fetchall()
        
#     except Exception as e:
#         # Esto capturará el error de MySQL y lo devolverá como 500
#         raise HTTPException(status_code=500, detail=f"DB Error al obtener valores (Verifique la sintaxis SQL): {str(e)}")
#     finally:
#         if conn: conn.close()