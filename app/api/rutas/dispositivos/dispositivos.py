from fastapi import Path, APIRouter, Query, HTTPException, Depends, status # 🚨 Añadido Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Dict, Any, Optional
import pymysql

# 🚨 Importaciones CRÍTICAS de Utilidades JWT
from app.servicios.auth_utils import get_current_user_id 
from app.configuracion import configuracion
from app.servicios.servicio_simulacion import get_db_connection, simular_datos_json
from app.api.modelos.dispositivos import DispositivoCrear, DispositivoActualizar,Dispositivo, Sensor, CampoSensor,DispositivoGeneral
from app.servicios import servicio_simulacion as servicio_simulacion 

router_dispositivo = APIRouter()

# ------------------------------------------------------------------
# 1. ENDPOINTS DE GESTIÓN (PROTEGIDOS)
# ------------------------------------------------------------------

# Crear Dispositivos (PROTEGIDO)
@router_dispositivo.post("/dispositivos/")
async def crear_Dispositivo(
    datos: DispositivoCrear,
    current_user_id: int = Depends(get_current_user_id) # 🚨 PROTEGIDO
):
    try:
        # Nota: Aquí se debería verificar que el current_user_id sea propietario del proyecto.
        resultados = await set_dispositivo(datos)
        return {"message": "Se registro el dispositivo", "resultados": resultados}

    except ValueError as e:
        return {"message": "Error en los datos enviados", "details": str(e)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error inesperado durante la inserción ", "details": str(e)},)



    
# Eliminar dispositivo (RUTA CORREGIDA Y PROTEGIDA) 
@router_dispositivo.delete("/dispositivos/")
async def eliminar_dispositivo_endpoint(
    id: Optional[int] = Query(..., description="ID del dispositivo a eliminar"),
    proyecto_id: int = Query(..., description="ID del proyecto"),
    current_user_id: int = Depends(get_current_user_id) # 🚨 PROTEGIDO
) -> Dict:
    # Nota: Se debería verificar que el current_user_id sea propietario del proyecto_id
    try:
        # Llama a la función de servicio de DB
        return await eliminar_dispositivo_db(id, proyecto_id) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar dispositivo(s): {str(e)}")


@router_dispositivo.get("/dispositivos/todos", response_model=List[DispositivoGeneral])
async def get_all_dispositivos_general(
    current_user_id: int = Depends(get_current_user_id) 
):
    try:
        # 🚨 Llamada a la función de DB
        dispositivos = await obtener_dispositivos_globales_db(current_user_id) 
        
        if not dispositivos:
            raise HTTPException(status_code=404, detail="No se encontraron dispositivos en la base de datos.")
        
        return dispositivos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener dispositivos globales: {str(e)}")


# NUEVO ENDPOINT PROTEGIDO
@router_dispositivo.get("/dispositivos/{dispositivo_id}/resumen")
async def get_dispositivo_resumen(
    dispositivo_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Obtiene un resumen de métricas clave para un dispositivo específico.
    """
    try:
        # 🚨 CORRECCIÓN: Llamar a la función de servicio
        resumen = await get_resumen_dispositivo_db(dispositivo_id)
        
        if not resumen:
            # Si la función de DB no devuelve nada, o devuelve un error, se maneja aquí.
            raise HTTPException(status_code=404, detail="Resumen no encontrado o dispositivo no existe.")
            
        return resumen
        
    except HTTPException:
        # Esto captura los errores 404/403 lanzados desde dentro o antes de la función de DB
        raise
    except Exception as e:
        # Esto captura los errores 500 lanzados desde la función de DB
        print(f"Error en el endpoint /dispositivos/{dispositivo_id}/resumen: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al procesar el resumen: {str(e)}")   
 
 
# Actualizar información de dispositivos (CORREGIDO Y PROTEGIDO)
@router_dispositivo.put("/dispositivos/{dispositivo_id}") # 🚨 RUTA CORREGIDA: Usando Path parameter
async def endpoint_actualizar_dispositivo(
    dispositivo_id: int, 
    datos: DispositivoActualizar,
    current_user_id: int = Depends(get_current_user_id) # 🚨 PROTEGIDO
):
    # Nota: Aquí se debería verificar que el current_user_id sea propietario del proyecto.
    try:
        resultados = await actualizar_datos_dispositivo(dispositivo_id, datos) # Llama a la función de DB
        return {"message": "Actualización de datos completada.", "resultados": resultados}

    except ValueError as e:
        return {"message": "Error en los datos enviados", "details": str(e)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "Error inesperado durante la actualización", "details": str(e)},)
    
# ------------------------------------------------------------------
# 2. ENDPOINTS DE CONSULTA (PROTEGIDOS)
# ------------------------------------------------------------------

# app/api/rutas/dispositivos/dispositivos.py (ENDPOINT ACTUALIZADO)

# Obtener todos los dispositivos de un proyecto (RUTA QUE LLAMA VUE)
@router_dispositivo.get("/dispositivos/proyecto/{proyecto_id}", response_model=List[Dispositivo])
async def get_dispositivos_por_proyecto(
    proyecto_id: int,
    current_user_id: int = Depends(get_current_user_id) # 🚨 PROTEGIDO
):
    # Nota: Aquí se debería verificar que el current_user_id tenga acceso al proyecto_id.
    
    # 🚨 CAMBIO CRÍTICO: Llamamos a la función integrada
    try:
        dispositivos = await obtener_dispositivos_por_proyecto_db(proyecto_id) 
        
        if not dispositivos:
            raise HTTPException(status_code=404, detail="No se encontraron dispositivos para este proyecto.")
        
        return dispositivos
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener dispositivos: {str(e)}")

# Obtener un dispositivo por ID
@router_dispositivo.get("/dispositivos/{dispositivo_id}", response_model=Dispositivo)
async def get_dispositivo_por_id(
    dispositivo_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    conn = None
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM dispositivos WHERE id = %s", (dispositivo_id,))
        dispositivo = cursor.fetchone()

        if not dispositivo:
            raise HTTPException(status_code=404, detail=f"Dispositivo con ID '{dispositivo_id}' no encontrado.")
        
        # 🚨 CORRECCIÓN CRÍTICA: Convertir datetime a string ANTES de retornar
        if 'fecha_creacion' in dispositivo and isinstance(dispositivo['fecha_creacion'], datetime):
            dispositivo['fecha_creacion'] = dispositivo['fecha_creacion'].strftime(DATE_FORMAT)

        # Nota: Aquí se debería verificar que el usuario tenga acceso al dispositivo
        return dispositivo

    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar el dispositivo: {str(e)}")
    finally:
        if conn: conn.close()
     

 
# app/api/rutas/dispositivos/dispositivos.py (ENDPOINT MODIFICADO)

# app/api/rutas/dispositivos/dispositivos.py (Fragmento de la ruta principal)


# ------------------------------------------------------------------
# 3. FUNCIONES DE BASE DE DATOS (SERVICIO DE DATOS BASE)
# ------------------------------------------------------------------

# Crear dispositivo
async def set_dispositivo(datos: DispositivoCrear) -> List[Dict[str, Any]]:
    # ... (cuerpo de la función set_dispositivo que ya tenías) ...
    procesado = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Validar existencia del proyecto
        cursor.execute("SELECT id FROM proyectos WHERE id = %s", (datos.proyecto_id,))
        proyecto_row = cursor.fetchone()
        if not proyecto_row:
            return [{"status": "error", "message": f"El proyecto con id: '{datos.proyecto_id}' no existe"}]
        
        fecha_creacion = datos.fecha_creacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar el dispositivo
        cursor.execute("INSERT INTO dispositivos (nombre, descripcion, tipo, latitud, longitud, habilitado, fecha_creacion, proyecto_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (
            datos.nombre, datos.descripcion, datos.tipo, datos.latitud, datos.longitud, datos.habilitado, fecha_creacion, datos.proyecto_id
        ))
        conn.commit()
        procesado.append({"nombre": datos.nombre, "status": "success", "id_insertado": conn.insert_id()})

    except pymysql.MySQLError as e:
        if conn: conn.rollback()
        procesado.append({"status": "error", "message": f"DB Error: {str(e)}"})
    except Exception as e:
        if conn: conn.rollback()
        procesado.append({"status": "error", "message": f"Unexpected Error: {str(e)}"})
    finally:
        if conn: conn.close()
    return procesado


# Función para actualizar datos del dispositivo (CORREGIDO)
async def actualizar_datos_dispositivo(dispositivo_id: int, datos: DispositivoActualizar) -> List[Dict[str, Any]]:
    procesado = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Validar existencia del dispositivo
        cursor.execute("SELECT * FROM dispositivos WHERE id = %s", (dispositivo_id,))
        if not cursor.fetchone():
            return [{"status": "error", "message": f"El dispositivo con id: '{dispositivo_id}' no existe"}]

        # Construir lista de campos a actualizar dinámicamente
        campos = []
        valores = []

        if datos.nombre is not None: campos.append("nombre = %s"); valores.append(datos.nombre)
        if datos.descripcion is not None: campos.append("descripcion = %s"); valores.append(datos.descripcion)
        if datos.tipo is not None: campos.append("tipo = %s"); valores.append(datos.tipo)
        if datos.latitud is not None: campos.append("latitud = %s"); valores.append(datos.latitud)
        if datos.longitud is not None: campos.append("longitud = %s"); valores.append(datos.longitud)
        if datos.habilitado is not None: campos.append("habilitado = %s"); valores.append(datos.habilitado)

        valores.append(dispositivo_id)

        if campos:
            sql = f"UPDATE dispositivos SET {', '.join(campos)} WHERE id = %s"
            cursor.execute(sql, valores)
            conn.commit()

            procesado.append({"status": "success", "message": f"Dispositivo con id '{dispositivo_id}' actualizado correctamente", "actualizado": datos.model_dump(exclude_none=True)})
        else:
            procesado.append({"status": "warning", "message": "No se proporcionaron datos para actualizar"})

    except Exception as e:
        if conn: conn.rollback()
        procesado.append({"status": "error", "message": f"Unexpected Error: {str(e)}"})
    finally:
        if conn: conn.close()
    return procesado


# Función de Eliminación de Dispositivo
async def eliminar_dispositivo_db(id: Optional[int], proyecto_id: int) -> Dict:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 🚨 Lógica de eliminación en cascada de Dispositivos (corregida)
        cursor.execute("SELECT * FROM proyectos WHERE id = %s", (proyecto_id,))
        if not cursor.fetchone(): raise HTTPException(status_code=404, detail=f"El proyecto con id: '{proyecto_id}' no existe")

        cursor_dict = conn.cursor(pymysql.cursors.DictCursor)
        
        if id is not None:
            # Eliminar un solo dispositivo si pertenece al proyecto
            cursor_dict.execute("SELECT id FROM dispositivos WHERE id = %s AND proyecto_id = %s", (id, proyecto_id))
        else:
            # Eliminar todos los dispositivos del proyecto
            cursor_dict.execute("SELECT id FROM dispositivos WHERE proyecto_id = %s", (proyecto_id,))
            
        dispositivos = cursor_dict.fetchall()
        if not dispositivos: raise HTTPException(status_code=404, detail="No se encontraron dispositivos para eliminar")

        for dispositivo in dispositivos:
            dispositivo_id = dispositivo["id"]
            
            # 1. Obtener y eliminar campos/valores (Hojas)
            cursor_dict.execute("SELECT id FROM sensores WHERE dispositivo_id = %s", (dispositivo_id,))
            sensores = cursor_dict.fetchall()

            for sensor in sensores:
                sensor_id = sensor["id"]
                # Eliminar valores y campos (asumimos que la lógica es compleja y la simplificamos)
                cursor.execute("DELETE FROM valores WHERE campo_id IN (SELECT id FROM campos_sensores WHERE sensor_id = %s)", (sensor_id,))
                cursor.execute("DELETE FROM campos_sensores WHERE sensor_id = %s", (sensor_id,))
            
            # 2. Eliminar Sensores
            cursor.execute("DELETE FROM sensores WHERE dispositivo_id = %s", (dispositivo_id,))
            
            # 3. Eliminar Dispositivo
            cursor.execute("DELETE FROM dispositivos WHERE id = %s", (dispositivo_id,))

        conn.commit()
        return {"status": "success", "message": f"{len(dispositivos)} dispositivo(s) eliminado(s) correctamente."}

    except Exception as e:
        if conn: conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar dispositivo(s): {str(e)}")
    finally:
        if conn: conn.close()
        


async def obtener_dispositivos_por_proyecto_db(proyecto_id: int) -> List[Dict[str, Any]]:
    conn = None
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S" # Definir el formato de fecha
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        sql = """
        SELECT id, nombre, descripcion, tipo, latitud, longitud, habilitado, fecha_creacion, proyecto_id
        FROM dispositivos 
        WHERE proyecto_id = %s
        """
        cursor.execute(sql, (proyecto_id,))
        dispositivos = cursor.fetchall()
        
        # 🚨 CORRECCIÓN CRÍTICA: Iterar y convertir datetime a string
        for disp in dispositivos:
            # Convertir habilitado a booleano (si no lo hace el ORM)
            if 'habilitado' in disp:
                disp['habilitado'] = disp['habilitado'] == 1 
            
            # 🚨 CONVERSIÓN DE FECHA
            if 'fecha_creacion' in disp and isinstance(disp['fecha_creacion'], datetime):
                disp['fecha_creacion'] = disp['fecha_creacion'].strftime(DATE_FORMAT)
                
        return dispositivos
        
    except Exception as e:
        print(f"Error al obtener dispositivos: {e}") 
        raise HTTPException(status_code=500, detail=f"Error en DB: {str(e)}")
        
    finally:
        if conn:
            conn.close()



async def obtener_dispositivos_globales_db(current_user_id: int) -> List[Dict[str, Any]]:
    conn = None
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 🚨 CONSULTA CRÍTICA: La misma consulta que funciona (filtrada por usuario)
        sql = """
        SELECT 
        DISTINCT d.id, d.nombre, d.descripcion, d.tipo, d.latitud, d.longitud, d.habilitado, d.fecha_creacion, d.proyecto_id, 
        p.nombre AS nombre_proyecto, p.usuario_id AS propietario_id
        FROM 
            dispositivos d
        JOIN 
            proyectos p ON d.proyecto_id = p.id
        LEFT JOIN 
            proyecto_usuarios pu ON p.id = pu.proyecto_id
        WHERE 
            p.usuario_id = %s OR pu.usuario_id = %s;
        """
        
        cursor.execute(sql, (current_user_id, current_user_id)) 
        dispositivos = cursor.fetchall()
        
        for disp in dispositivos:
            # 1. Convertir habilitado (0/1) a booleano (CORRECTO)
            if 'habilitado' in disp:
                disp['habilitado'] = int(disp['habilitado']) == 1 
            
            # 2. CONVERSIÓN DE FECHA (datetime -> str)
            # 🚨 CRÍTICO: Comprobar el tipo de objeto explícitamente.
            if 'fecha_creacion' in disp and isinstance(disp['fecha_creacion'], datetime):
                disp['fecha_creacion'] = disp['fecha_creacion'].strftime(DATE_FORMAT)

            # 3. Mapeo de Nulos para Double (latitud/longitud)
            # Aseguramos que los valores nulos que la DB devuelve sean None si no son números.
            if disp.get('latitud') is not None:
                disp['latitud'] = float(disp['latitud']) 
            if disp.get('longitud') is not None:
                disp['longitud'] = float(disp['longitud'])


        return dispositivos

    except Exception as e:
        print(f"Error en DB al obtener dispositivos globales: {e}")
        # 🚨 Retornamos el 500 con detalle para el usuario si es un fallo de DB
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
        
    finally:
        if conn:
            conn.close()

async def get_resumen_dispositivo_db(dispositivo_id: int) -> Dict[str, Any]:
#esa es la forma que debe devolver el resumen 
#     {
#     "ultima_conexion": "2025-10-23T17:15:18",
#     "total_dispositivos": 2,
#     "total_sensores": 4,
#     "campos_activos": 7,
#     "estado_dispositivo": "Activo"
# }
    conn = None
    try:
        conn = get_db_connection()
        # 🚨 CORRECCIÓN: Usar DictCursor para todas las consultas
        cursor = conn.cursor(pymysql.cursors.DictCursor) 
        
        # 1. Obtener la Última Conexión
        sql_ultima_conexion = """
        SELECT MAX(v.fecha_hora_lectura) AS ultima_conexion_dt
        FROM valores v
        JOIN campos_sensores cs ON v.campo_id = cs.id
        JOIN sensores s ON cs.sensor_id = s.id
        WHERE s.dispositivo_id = %s;
        """
        cursor.execute(sql_ultima_conexion, (dispositivo_id,))
        resultado_conexion = cursor.fetchone()
        # 🚨 CORRECCIÓN: Manejar el caso de que no haya conexión (resultado None)
        ultima_conexion = resultado_conexion['ultima_conexion_dt'] if resultado_conexion else None
        
        # 2. Obtener Campos Activos
        sql_campos_activos = """
        SELECT COUNT(DISTINCT cs.id) AS count_campos_activos
        FROM campos_sensores cs
        JOIN sensores s ON cs.sensor_id = s.id
        WHERE s.dispositivo_id = %s
          AND cs.id IN (SELECT DISTINCT campo_id FROM valores);
        """
        cursor.execute(sql_campos_activos, (dispositivo_id,))
        # 🚨 CORRECCIÓN: Manejar el caso de que no haya campos (resultado None)
        resultado_campos = cursor.fetchone()
        campos_activos_count = resultado_campos['count_campos_activos'] if resultado_campos else 0

        # 3. Obtener Totales
        sql_totales = """
        SELECT 
            (SELECT COUNT(*) FROM dispositivos WHERE proyecto_id = 
                (SELECT proyecto_id FROM dispositivos WHERE id = %s)) AS total_dispositivos,
            (SELECT COUNT(*) FROM sensores WHERE dispositivo_id = %s) AS total_sensores;
        """
        cursor.execute(sql_totales, (dispositivo_id, dispositivo_id))
        totales_dict = cursor.fetchone() # Ahora sí es un diccionario

        # 4. Formatear el resultado
        return {
            "ultima_conexion": ultima_conexion.isoformat() if ultima_conexion else None,
            "total_dispositivos": totales_dict['total_dispositivos'] if totales_dict else 0,
            "total_sensores": totales_dict['total_sensores'] if totales_dict else 0,
            "campos_activos": campos_activos_count,
            "estado_dispositivo": "Activo" # Placeholder
        }

    except Exception as e:
        print(f"Error al obtener resumen de dispositivo: {e}")
        # Lanzar la excepción para que el endpoint la maneje como 500
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")
    finally:
        if conn: conn.close()