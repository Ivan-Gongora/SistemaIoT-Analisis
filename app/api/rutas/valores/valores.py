from fastapi import Path, Body
from fastapi import APIRouter, Query, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymysql
from app.servicios.auth_utils import get_current_user_id # Solo autenticación


from app.configuracion import configuracion
from app.servicios.servicio_simulacion import get_db_connection, simular_datos_json
from app.api.modelos.simulacionJson import DatosSimulacionJson

from app.api.modelos.valores import Valor

from app.api.modelos.simulacion import DatosSimulacion



router = APIRouter()

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
@router.get("/valores/historico-campo/{campo_id}", response_model=List[Valor])
async def get_valores_historicos(
    campo_id: int,
    fecha_inicio: Optional[datetime] = Query(None, description="Filtro de fecha inicial (ISO 8601)"),
    fecha_fin: Optional[datetime] = Query(None, description="Filtro de fecha final (ISO 8601)"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Obtiene los registros históricos de un campo de sensor específico,
    permitiendo filtrar por rango de fechas.
    """
    try:
        valores = await obtener_valores_por_campo_db(campo_id, fecha_inicio, fecha_fin)
        
        # Si no se encuentran valores, devolvemos una lista vacía (200 OK).
        if not valores:
            return []
        
        return valores
        
    except HTTPException:
        raise
    except Exception as e:
        # En caso de error de DB o cualquier otro, devolvemos 500
        raise HTTPException(status_code=500, detail=f"Error al obtener valores: {str(e)}")

# ----------------------------------------------------------------------
# FUNCIONES DE SERVICIO DE BASE DE DATOS
# ----------------------------------------------------------------------

async def obtener_valores_por_campo_db(
    campo_id: int, 
    fecha_inicio: Optional[datetime] = None, 
    fecha_fin: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # ✅ CONSULTA CORREGIDA: Usando fecha_hora_registro en lugar de fecha_dispositivo
        sql = """
        SELECT
            v.id,
            v.valor,
            v.fecha_hora_lectura,
            v.fecha_hora_registro,  -- ✅ CORREGIDO: fecha_hora_registro existe
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
        """
        params = [campo_id]
        
        if fecha_inicio:
            sql += " AND v.fecha_hora_lectura >= %s"
            params.append(fecha_inicio)
        if fecha_fin:
            sql += " AND v.fecha_hora_lectura <= %s"
            params.append(fecha_fin)
            
        sql += " ORDER BY v.fecha_hora_lectura ASC;"
        
        cursor.execute(sql, params)
        return cursor.fetchall()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error al obtener valores: {str(e)}")
    finally:
        if conn: conn.close()


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