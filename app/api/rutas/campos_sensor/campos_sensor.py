# app/api/rutas/campos_sensores.py

from fastapi import APIRouter, Query, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import pymysql

from app.servicios.auth_utils import get_current_user_id
from app.servicios.servicio_simulacion import get_db_connection
from app.api.modelos.campos_sensores import CampoSensor, CampoSensorCrear, CampoSensorActualizar

router_campos = APIRouter()

# ----------------------------------------------------------------------
# FUNCIONES DE SERVICIO DE BASE DE DATOS
# ----------------------------------------------------------------------

# GET: Obtener campos por sensor_id (con datos de unidad)
# async def obtener_campos_por_sensor_db(sensor_id: int) -> List[Dict[str, Any]]:
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
        
#         sql = """
#         SELECT 
#             cs.id, cs.nombre, cs.tipo_valor, cs.sensor_id, cs.unidad_medida_id, 
#             um.nombre AS nombre_unidad, 
#             um.simbolo AS simbolo_unidad,
#             um.magnitud_tipo,
#             (
#                 SELECT v.valor 
#                 FROM valores v 
#                 WHERE v.campo_id = cs.id 
#                 ORDER BY v.fecha_hora_lectura DESC 
#                 LIMIT 1
#             ) AS ultimo_valor
#         FROM campos_sensores cs
#         LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
#         WHERE cs.sensor_id = %s;
#         """
#         cursor.execute(sql, (sensor_id,))
#         return cursor.fetchall()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"DB Error al obtener campos: {str(e)}")
#     finally:
#         if conn: conn.close()
        # app/api/rutas/campos_sensor/campos_sensor.py (Función de servicio)
#23/10/2025
#lo que hay arriba es la version que si funciona con la vista de : TarjetaCampoSensor.vue,habra que actualizarlo para que funcione con la nueva version
# app/api/rutas/campos_sensor/campos_sensor.py (Función de servicio)

async def obtener_campos_por_sensor_db(sensor_id: int) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        sql = """
        SELECT 
            cs.id, cs.nombre, cs.tipo_valor, cs.sensor_id, cs.unidad_medida_id, 
            um.nombre AS nombre_unidad, 
            um.simbolo AS simbolo_unidad,
            um.magnitud_tipo,
            (
                SELECT v.valor 
                FROM valores v 
                WHERE v.campo_id = cs.id 
                ORDER BY v.fecha_hora_lectura DESC 
                LIMIT 1
            ) AS ultimo_valor  -- ✅ MANTENER como Decimal, el modelo lo maneja
        FROM campos_sensores cs
        LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
        WHERE cs.sensor_id = %s;
        """
        cursor.execute(sql, (sensor_id,))
        
        return cursor.fetchall()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error al obtener campos: {str(e)}")
    finally:
        if conn: conn.close()
        
        
# POST: Crear un nuevo campo
async def set_campo_sensor_db(datos: CampoSensorCrear) -> Dict[str, Any]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validaciones (Sensor padre y Unidad de medida)
        cursor.execute("SELECT id FROM sensores WHERE id = %s", (datos.sensor_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Sensor padre no encontrado.")
            
        cursor.execute("SELECT id FROM unidades_medida WHERE id = %s", (datos.unidad_medida_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Unidad de medida no encontrada.")

        # Insertar el campo
        cursor.execute(
            "INSERT INTO campos_sensores (nombre, tipo_valor, sensor_id, unidad_medida_id) VALUES (%s, %s, %s, %s)",
            (datos.nombre, datos.tipo_valor, datos.sensor_id, datos.unidad_medida_id)
        )
        conn.commit()
        return {"status": "success", "id_insertado": conn.insert_id(), "nombre": datos.nombre}
    
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al insertar campo: {str(e)}")
    finally:
        if conn: conn.close()

# PUT: Actualizar un campo de sensor
async def actualizar_campo_sensor_db(id: int, datos: CampoSensorActualizar) -> Dict[str, Any]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        campos = []
        valores = []
        
        if datos.nombre is not None: campos.append("nombre = %s"); valores.append(datos.nombre)
        if datos.tipo_valor is not None: campos.append("tipo_valor = %s"); valores.append(datos.tipo_valor)
        if datos.unidad_medida_id is not None: campos.append("unidad_medida_id = %s"); valores.append(datos.unidad_medida_id)
        
        if not campos:
             return {"status": "warning", "message": "No se proporcionaron datos para actualizar"}
             
        valores.append(id)
        sql = f"UPDATE campos_sensores SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(sql, valores)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Campo de sensor no encontrado.")
        
        return {"status": "success", "rows_affected": cursor.rowcount}
    except pymysql.Error as e:
        raise HTTPException(status_code=500, detail=f"DB Error al actualizar campo: {str(e)}")
    finally:
        if conn: conn.close()

# DELETE: Eliminar un campo de sensor
async def eliminar_campo_sensor_db(id: int) -> Dict[str, Any]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Eliminar valores asociados (Hoja)
        cursor.execute("DELETE FROM valores WHERE campo_id = %s", (id,))
        
        # 2. Eliminar el campo
        cursor.execute("DELETE FROM campos_sensores WHERE id = %s", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Campo de sensor no encontrado.")
            
        return {"status": "success", "message": "Campo de sensor eliminado exitosamente."}
    except pymysql.Error as e:
        if e.args[0] == 1451: # Error de FK (si valores falla)
             raise HTTPException(status_code=400, detail="No se puede eliminar: El campo aún tiene valores asociados.")
        raise HTTPException(status_code=500, detail=f"DB Error al eliminar campo: {str(e)}")
    finally:
        if conn: conn.close()

# ----------------------------------------------------------------------
# ENDPOINTS (Protegidos por JWT)
# ----------------------------------------------------------------------

# GET (Ya lo tienes en el router de sensores, lo movemos aquí)
@router_campos.get("/sensores/{sensor_id}/campos", response_model=List[CampoSensor])
async def get_campos_por_sensor(
    sensor_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    # NOTA: Aquí iría la autorización (check_user_permission)
    try:
        campos = await obtener_campos_por_sensor_db(sensor_id)
        if not campos:
            raise HTTPException(status_code=404, detail="No se encontraron campos para este sensor.")
        return campos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener campos: {str(e)}")

# POST (Crear)
@router_campos.post("/campos_sensores/", response_model=Dict[str, Any])
async def crear_campo_sensor(
    datos: CampoSensorCrear,
    current_user_id: int = Depends(get_current_user_id)
):
    # NOTA: Autorización
    try:
        resultado = await set_campo_sensor_db(datos)
        return {"message": "Campo de sensor creado exitosamente.", "resultados": resultado}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear campo: {str(e)}")

# PUT (Actualizar)
@router_campos.put("/campos_sensores/{id}", response_model=Dict[str, Any])
async def actualizar_campo_sensor(
    id: int,
    datos: CampoSensorActualizar,
    current_user_id: int = Depends(get_current_user_id)
):
    # NOTA: Autorización
    try:
        return await actualizar_campo_sensor_db(id, datos)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar campo: {str(e)}")

# DELETE (Eliminar)
@router_campos.delete("/campos_sensores/{id}", response_model=Dict[str, Any])
async def eliminar_campo_sensor(
    id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    # NOTA: Autorización
    try:
        return await eliminar_campo_sensor_db(id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar campo: {str(e)}")