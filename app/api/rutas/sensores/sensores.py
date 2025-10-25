# app/api/rutas/sensores/sensores.py (Fragmento)

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Dict, Any, Optional
import pymysql

# 🚨 Importaciones de Modelos y Utilidades
from app.servicios.auth_utils import get_current_user_id # Solo autenticación
from app.servicios.servicio_simulacion import get_db_connection
from app.api.modelos.sensores import SensorCrear,Sensor, SensorActualizar, SensorGeneral

router_sensor = APIRouter()

# ----------------------------------------------------------------------
# ENDPOINT DE CREACIÓN
# ----------------------------------------------------------------------

# POST: Crear Sensor (Requiere JWT)
@router_sensor.post("/sensores/")
async def crear_sensor_endpoint(
    datos: SensorCrear,
    current_user_id: int = Depends(get_current_user_id) # Usado para autenticación
):
    try:
        resultados = await set_sensor(datos)
        return {"message": "Sensor registrado exitosamente.", "resultados": resultados}
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error inesperado", "details": str(e)})

# GET: Obtener todos los sensores accesibles para el usuario (propietario o miembro)
@router_sensor.get("/sensores/todos", response_model=List[SensorGeneral])
async def get_all_sensores_general(
    current_user_id: int = Depends(get_current_user_id) 
):
  
    try:
        sensores = await obtener_sensores_globales_db(current_user_id) 
        
        if not sensores:
            raise HTTPException(status_code=404, detail="No se encontraron sensores para este usuario.")
        
        return sensores
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sensores globales: {str(e)}")

# GET: Obtener Sensor por ID (Requiere JWT)
@router_sensor.get("/sensores/{id}", response_model=Sensor)
async def get_sensor_por_id(
    id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        sensor = await obtener_sensor_por_id_db(id)
        if not sensor:
            raise HTTPException(status_code=404, detail="Sensor no encontrado.")
        # Nota: Aquí se debería verificar que el usuario tenga acceso al dispositivo/proyecto.
        
        return sensor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sensor: {str(e)}")
    

# GET: Obtener Sensores por Dispositivo (Requiere JWT)
@router_sensor.get("/sensores/dispositivo/{dispositivo_id}", response_model=List[Sensor])
async def get_sensores_por_dispositivo(
    dispositivo_id: int,
    current_user_id: int = Depends(get_current_user_id) # 🚨 AUTENTICACIÓN
):
    # Nota: Aquí se debería verificar que el usuario tenga acceso al dispositivo/proyecto.
    
    try:
        sensores = await obtener_sensores_por_dispositivo_db(dispositivo_id)
        if not sensores:
            raise HTTPException(status_code=404, detail="No se encontraron sensores para este dispositivo.")
        return sensores
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sensores: {str(e)}")

# PUT: Actualizar Sensor (Requiere JWT)
@router_sensor.put("/sensores/{id}")
async def actualizar_sensor_endpoint(
    id: int,
    datos: SensorActualizar,
    current_user_id: int = Depends(get_current_user_id)
):
    try:
        # 1. Ejecutar la actualización (db_function ya existe)
        await actualizar_sensor_db(id, datos)
        
        # 2. 🚨 CRÍTICO: Obtener y devolver el objeto completo y actualizado
        sensor_actualizado = await obtener_sensor_por_id_db(id)
        
        if not sensor_actualizado:
             raise HTTPException(status_code=404, detail="Sensor actualizado no encontrado para devolver.")
             
        # Envuelve el resultado en un diccionario para imitar el patrón de respuesta de otras rutas
        return {"status": "success", "resultados": [sensor_actualizado]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar sensor: {str(e)}")


# DELETE: Eliminar Sensor (Requiere JWT)
@router_sensor.delete("/sensores/{id}")
async def eliminar_sensor_endpoint(
    id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    # Nota: Aquí iría la verificación de permiso (CRUD_SENSOR)
    try:
        return await eliminar_sensor_db(id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar sensor: {str(e)}")

# ----------------------------------------------------------------------
# FUNCIONES DE SERVICIO DE BASE DE DATOS
# ----------------------------------------------------------------------

# POST: Insertar un nuevo sensor y sus campos asociados
async def set_sensor(datos: SensorCrear) -> Dict[str, Any]:
    conn = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
            # 🚨 CRÍTICO: IMPRIMIR EL PAYLOAD COMPLETO ANTES DE LA LÓGICA
        # Esto te mostrará la estructura real que el backend está viendo.
        print("-" * 50)
        print("PAYLOAD RECIBIDO DEL FRONTEND:")
        # Usamos .model_dump_json() para obtener el JSON completo como string
        print(datos.model_dump_json(indent=2)) 
        print("-" * 50)
            
        # 1. Validar existencia del dispositivo padre
        cursor.execute("SELECT id FROM dispositivos WHERE id = %s", (datos.dispositivo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Dispositivo con ID '{datos.dispositivo_id}' no encontrado.")
            
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. Insertar el sensor principal
        cursor.execute(
            """INSERT INTO sensores (nombre, tipo, habilitado, fecha_creacion, dispositivo_id) 
               VALUES (%s, %s, %s, %s, %s)""", 
            (datos.nombre, datos.tipo, datos.habilitado, fecha_creacion, datos.dispositivo_id)
        )
        
        # 3. 🚨 CRÍTICO: Obtener el ID del sensor recién insertado
        sensor_id = conn.insert_id()
        
        # 4. 🚨 ITERAR E INSERTAR CAMPOS DE SENSOR
        for campo in datos.campos:
            # Puedes omitir la validación de unidad_medida_id si ya confías en el frontend
            
            cursor.execute(
                """INSERT INTO campos_sensores (nombre, tipo_valor, sensor_id, unidad_medida_id) 
                   VALUES (%s, %s, %s, %s)""",
                (campo.nombre, campo.tipo_valor, sensor_id, campo.unidad_medida_id)
            )
        
        conn.commit()
        
        return {
            "status": "success", 
            "id_insertado": sensor_id, 
            "nombre": datos.nombre,
            "campos_agregados": len(datos.campos)
        }
    
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al insertar sensor/campos: {str(e)}")
    finally:
        if conn: conn.close()


# GET: Obtener Sensores por Dispositivo (Requiere JWT)
async def obtener_sensores_por_dispositivo_db(dispositivo_id: int) -> List[Dict[str, Any]]:
    conn = None
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S" 
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 🚨 CONSULTA CRÍTICA: Añadir el SUBQUERY para contar los campos
        sql = """
        SELECT 
            s.*, -- Selecciona todas las columnas base del sensor
            (
                SELECT COUNT(cs.id) 
                FROM campos_sensores cs 
                WHERE cs.sensor_id = s.id
            ) AS total_campos -- 👈 CRÍTICO: El contador
        FROM sensores s 
        WHERE s.dispositivo_id = %s;
        """
        
        cursor.execute(sql, (dispositivo_id,))
        sensores = cursor.fetchall()
        
        # 🚨 PROCESAMIENTO DE DATOS (Asegurar que total_campos sea int)
        for sensor in sensores:
            if 'habilitado' in sensor:
                sensor['habilitado'] = int(sensor['habilitado']) == 1 
            if 'fecha_creacion' in sensor and isinstance(sensor['fecha_creacion'], datetime):
                sensor['fecha_creacion'] = sensor['fecha_creacion'].strftime(DATE_FORMAT)
            
            # 🚨 Asegurar que el campo se castee a entero
            if 'total_campos' in sensor:
                # Se asegura de que se pase como int, no como string o Decimal
                sensor['total_campos'] = int(sensor['total_campos'])

        return sensores
        
    except Exception as e:
        print(f"Error al obtener sensores por dispositivo: {e}") 
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
        
    finally:
        if conn: conn.close()

# PUT: Actualizar un sensor
async def actualizar_sensor_db(id: int, datos: SensorActualizar) -> Dict[str, Any]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Validación de existencia
        cursor.execute("SELECT id FROM sensores WHERE id = %s", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Sensor no encontrado.")

        # 2. Construcción de UPDATE dinámico
        campos = []
        valores = []
        
        if datos.nombre is not None: campos.append("nombre = %s"); valores.append(datos.nombre)
        if datos.tipo is not None: campos.append("tipo = %s"); valores.append(datos.tipo)
        if datos.habilitado is not None: campos.append("habilitado = %s"); valores.append(datos.habilitado)
        
        if not campos:
             return {"status": "warning", "message": "No se proporcionaron datos para actualizar"}
             
        valores.append(id)
        sql = f"UPDATE sensores SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(sql, valores)
        conn.commit()
        
        return {"status": "success", "rows_affected": cursor.rowcount}
    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=f"DB Error al actualizar sensor: {str(e)}")
    finally:
        if conn: conn.close()

# DELETE: Eliminar un sensor (Y sus campos/datos)
async def eliminar_sensor_db(id: int) -> Dict[str, Any]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Lógica de Eliminación en Cascada (Hojas primero)
        
        # a) Eliminar VALORES (depende de campos_sensores)
        cursor.execute("DELETE FROM valores WHERE campo_id IN (SELECT id FROM campos_sensores WHERE sensor_id = %s)", (id,))
        
        # b) Eliminar CAMPOS DE SENSORES
        cursor.execute("DELETE FROM campos_sensores WHERE sensor_id = %s", (id,))
        
        # 2. Eliminar SENSOR
        cursor.execute("DELETE FROM sensores WHERE id = %s", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Sensor no encontrado.")
            
        return {"status": "success", "message": "Sensor eliminado exitosamente."}
    except pymysql.Error as e:
        if e.args[0] == 1451: # Si falla por otra clave foránea (no debería)
             raise HTTPException(status_code=400, detail="No se puede eliminar: El sensor aún tiene dependencias externas.")
        raise HTTPException(status_code=500, detail=f"DB Error al eliminar sensor: {str(e)}")
    finally:
        if conn: conn.close()

# GET: Obtener un sensor por ID
async def obtener_sensor_por_id_db(sensor_id: int) -> Dict[str, Any] | None:
    conn = None
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 🚨 CONSULTA: Obtener todos los detalles del sensor
        cursor.execute("SELECT * FROM sensores WHERE id = %s", (sensor_id,))
        sensor = cursor.fetchone()
        
        if sensor:
            # 🚨 Conversión de tipos (CRÍTICO para Pydantic)
            if 'habilitado' in sensor:
                sensor['habilitado'] = int(sensor['habilitado']) == 1
            if 'fecha_creacion' in sensor and isinstance(sensor['fecha_creacion'], datetime):
                sensor['fecha_creacion'] = sensor['fecha_creacion'].strftime(DATE_FORMAT)
        return sensor
    except Exception as e:
        print(f"Error al obtener sensor por ID: {e}")
        return None
    finally:
        if conn: conn.close()

# GET: Obtener todos los sensores accesibles para el usuario (propietario o miembro)
async def obtener_sensores_globales_db(current_user_id: int) -> List[Dict[str, Any]]:
    """
    Obtiene todos los sensores a los que un usuario tiene acceso (como propietario o miembro),
    incluyendo los nombres del dispositivo y proyecto.
    """
    conn = None
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 🚨 CONSULTA CRÍTICA: JOIN de 3 niveles (Sensor -> Dispositivo -> Proyecto)
        # Filtra por el usuario actual
        sql = """
        SELECT 
            DISTINCT 
            s.id, s.nombre, s.tipo, s.habilitado, s.fecha_creacion, s.dispositivo_id,
            d.nombre AS nombre_dispositivo,
            p.nombre AS nombre_proyecto,
            p.id AS proyecto_id,
            (SELECT COUNT(cs.id) FROM campos_sensores cs WHERE cs.sensor_id = s.id) AS total_campos
        FROM 
            sensores s
        JOIN 
            dispositivos d ON s.dispositivo_id = d.id
        JOIN 
            proyectos p ON d.proyecto_id = p.id
        LEFT JOIN 
            proyecto_usuarios pu ON p.id = pu.proyecto_id
        WHERE 
            p.usuario_id = %s OR pu.usuario_id = %s;
        """
        
        cursor.execute(sql, (current_user_id, current_user_id)) 
        sensores = cursor.fetchall()
        
        # Procesamiento de tipos (Booleano y Fecha)
        for sensor in sensores:
            if 'habilitado' in sensor:
                sensor['habilitado'] = int(sensor['habilitado']) == 1 
            if 'fecha_creacion' in sensor and isinstance(sensor['fecha_creacion'], datetime):
                sensor['fecha_creacion'] = sensor['fecha_creacion'].strftime(DATE_FORMAT)
            if 'total_campos' in sensor:
                sensor['total_campos'] = int(sensor['total_campos'])

        return sensores

    except Exception as e:
        print(f"Error en DB al obtener sensores globales: {e}")
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    finally:
        if conn:
            conn.close()
