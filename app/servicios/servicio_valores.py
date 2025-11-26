import pymysql
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.servicios.servicio_simulacion import get_db_connection, simular_datos_json

# -----------------------------------------------------------------------------
# 1. OBTENER ÚLTIMO VALOR (POLLING 5s)
# -----------------------------------------------------------------------------
async def obtener_ultimo_valor_db(campo_id: int) -> Optional[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        sql = """
        SELECT 
            uv.campo_id,
            uv.ultimo_valor AS valor,
            uv.fecha AS fecha_hora_lectura,
            cs.nombre AS nombre_campo,
            um.magnitud_tipo,
            um.simbolo AS simbolo_unidad
        FROM ultimo_valor_campo uv
        INNER JOIN campos_sensores cs ON uv.campo_id = cs.id
        LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
        WHERE uv.campo_id = %s;
        """
        cursor.execute(sql, (campo_id,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado
            
        return await _fallback_ultimo_valor_maestro(campo_id)

    except Exception as e:
        print(f"❌ [DB Error] obtener_ultimo_valor: {e}")
        return await _fallback_ultimo_valor_maestro(campo_id)
    finally:
        if conn: conn.close()

async def _fallback_ultimo_valor_maestro(campo_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql = """
        SELECT v.campo_id, v.valor, v.fecha_hora_lectura, 
               cs.nombre AS nombre_campo, um.magnitud_tipo, um.simbolo AS simbolo_unidad
        FROM valores v
        JOIN campos_sensores cs ON v.campo_id = cs.id
        LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
        WHERE v.campo_id = %s
        ORDER BY v.fecha_hora_lectura DESC LIMIT 1
        """
        cursor.execute(sql, (campo_id,))
        return cursor.fetchone()
    except Exception:
        return None
    finally:
        if conn: conn.close()

# -----------------------------------------------------------------------------
# 🧠 MOTOR DE ANÁLISIS 1: INDIVIDUAL (Tiempo Real / Polling)
# -----------------------------------------------------------------------------
async def detectar_anomalia_individual(campo_id: int, valor_actual: float) -> tuple[bool, Optional[str]]:
    """
    Detecta anomalías comparando con la historia reciente.
    MEJORA: Lógica adaptativa basada en el promedio histórico del propio sensor.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1. Contexto histórico (Traemos más datos para establecer un perfil base)
        # 300 registros ~ 25 minutos (a 5s/dato). Suficiente para ver la tendencia reciente.
        sql = """
        SELECT v.valor, cs.nombre, cs.tipo_valor 
        FROM valores v 
        JOIN campos_sensores cs ON v.campo_id = cs.id
        WHERE v.campo_id = %s 
        ORDER BY v.fecha_hora_lectura DESC 
        LIMIT 300
        """
        cursor.execute(sql, (campo_id,))
        rows = cursor.fetchall()
        
        if not rows or len(rows) < 20:
            return False, None # Insuficientes datos para aprender el patrón

        # Detección de Tipo
        tipo = (rows[0].get('tipo_valor') or '').lower()
        nombre = (rows[0].get('nombre') or '').lower()
        es_movimiento = 'bool' in tipo or 'movimiento' in nombre or 'estado' in nombre

        # --- RAMA A: ANÁLISIS DE MOVIMIENTO (FRECUENCIA ADAPTATIVA) ---
        if es_movimiento:
            # Ventana "Ahora" (Último minuto ~ 12 registros)
            ventana_reciente = rows[:12]
            actividad_actual = sum(float(r['valor']) for r in ventana_reciente) # Suma de 1s
            
            # Ventana "Base" (Los 24 minutos anteriores)
            historia_base = rows[12:]
            
            # Calculamos el promedio de actividad por minuto en el pasado
            # Agrupamos en bloques de 12 (1 min)
            bloques = [historia_base[i:i + 12] for i in range(0, len(historia_base), 12)]
            sumas_bloques = [sum(float(r['valor']) for r in b) for b in bloques]
            
            # Promedio histórico de eventos por minuto
            promedio_actividad = sum(sumas_bloques) / len(sumas_bloques) if sumas_bloques else 0
            
            # --- REGLAS DINÁMICAS ---
            
            # Caso 1: Lugar Tranquilo (Promedio < 2 eventos/min)
            if promedio_actividad < 2:
                # Si de repente hay mucha actividad (> 8 eventos/min), es anomalía clara.
                if actividad_actual > 8:
                    return True, f"Actividad Inusual ({int(actividad_actual)} eventos/min vs normal bajo)"

            # Caso 2: Lugar Concurrido (Promedio > 10 eventos/min)
            elif promedio_actividad > 10:
                # Si la actividad se triplica (Fiesta/Multitud)
                if actividad_actual > (promedio_actividad * 3):
                    return True, f"Pico de Tráfico ({int(actividad_actual)} eventos vs media {int(promedio_actividad)})"
                # Si la actividad cae a 0 de golpe (Fallo de sensor o cierre inesperado)
                # Solo si es 0 absoluto en el último minuto
                if actividad_actual == 0:
                    return True, "Caída de Actividad (0 eventos detectados)"
            
            # Caso 3: Intermedio (Regla general 3x)
            else:
                if actividad_actual > (max(promedio_actividad, 2) * 3):
                    return True, f"Alta Actividad ({int(actividad_actual)} eventos)"
            
            return False, None

        # --- RAMA B: ANÁLISIS NUMÉRICO (Z-SCORE) ---
        else:
            # Tomamos solo los últimos 60 para Z-Score (5 min) para que sea sensible
            datos_z = rows[:60]
            historial = [float(r['valor']) for r in datos_z]
            
            ventana_reciente = historial[:3] 
            valor_suavizado = sum(ventana_reciente) / len(ventana_reciente)
            
            linea_base = historial[3:]
            if not linea_base: return False, None

            media_base = sum(linea_base) / len(linea_base)
            varianza = sum([((x - media_base) ** 2) for x in linea_base]) / len(linea_base)
            desviacion = math.sqrt(varianza)

            if desviacion < 0.1: desviacion = 0.1

            z_score = (valor_suavizado - media_base) / desviacion
            UMBRAL = 3.0 

            if abs(z_score) > UMBRAL:
                tipo_pico = "ALTO" if z_score > 0 else "BAJO"
                return True, f"Pico {tipo_pico} anómalo ({valor_suavizado:.1f})"
            
            return False, None

    except Exception as e:
        print(f"⚠️ Error análisis realtime: {e}")
        return False, None
    finally:
        if conn: conn.close()


# -----------------------------------------------------------------------------
# 🧠 MOTOR DE ANÁLISIS 2: POR LOTES (Carga Inicial / Ventana)
# -----------------------------------------------------------------------------
def aplicar_analisis_anomalias(datos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Procesa un lote completo de datos (ej. las últimas 24h) para marcar picos pasados.
    """
    if not datos or len(datos) < 10: return datos

    # Detectar tipo basado en el primer registro
    es_movimiento = False
    if datos[0].get('nombre_campo'):
        nombre = datos[0]['nombre_campo'].lower()
        es_movimiento = 'movimiento' in nombre or 'estado' in nombre or 'puerta' in nombre

    if es_movimiento:
        # Lógica para Movimiento en Lotes (Barras)
        valores = [float(d['valor']) for d in datos]
        media_total = sum(valores) / len(valores)
        
        # Si el promedio general es muy bajo (poca actividad), cualquier ráfaga es anomalía.
        umbral_actividad = max(media_total * 3, 5) # Mínimo 5 eventos para considerar alerta

        for d in datos:
            val = float(d['valor'])
            d['anomalia'] = False
            d['mensaje_alerta'] = None
            
            if val > umbral_actividad: 
                d['anomalia'] = True
                d['mensaje_alerta'] = f"Pico de Actividad ({int(val)} eventos)"

    else:
        # Lógica Z-Score Estándar (Temperatura, etc.)
        valores = [float(d['valor']) for d in datos]
        media = sum(valores) / len(valores)
        varianza = sum([((x - media) ** 2) for x in valores]) / len(valores)
        desviacion_std = math.sqrt(varianza)
        
        if desviacion_std < 0.01: desviacion_std = 0.01
        UMBRAL_Z = 2.8 

        for d in datos:
            val = float(d['valor'])
            z_score = (val - media) / desviacion_std
            d['anomalia'] = False
            d['mensaje_alerta'] = None

            if abs(z_score) > UMBRAL_Z:
                d['anomalia'] = True
                d['mensaje_alerta'] = f"Valor atípico: {val}"
    
    return datos

# -----------------------------------------------------------------------------
# 2. VENTANA DE TIEMPO (Ancla en último dato)
# -----------------------------------------------------------------------------
async def obtener_valores_ventana_db(campo_id: int, minutos: int) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        sql_ancla = "SELECT fecha FROM ultimo_valor_campo WHERE campo_id = %s"
        cursor.execute(sql_ancla, (campo_id,))
        res_ancla = cursor.fetchone()
        
        if not res_ancla:
            cursor.execute("SELECT MAX(fecha_hora_lectura) as fecha FROM valores WHERE campo_id = %s", (campo_id,))
            res_ancla = cursor.fetchone()
            
        if not res_ancla or not res_ancla['fecha']:
            return [] 

        fecha_fin = res_ancla['fecha']
        print(f"⏱️ [DB] Ventana {minutos} min. Ancla: {fecha_fin}")

        sql = """
        SELECT * FROM (
            SELECT 
                v.valor, 
                v.fecha_hora_lectura,
                um.magnitud_tipo,
                um.simbolo AS simbolo_unidad,
                cs.nombre AS nombre_campo
            FROM valores v
            JOIN campos_sensores cs ON v.campo_id = cs.id
            LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
            WHERE v.campo_id = %s 
              AND v.fecha_hora_lectura >= (%s - INTERVAL %s MINUTE)
              AND v.fecha_hora_lectura <= %s
            ORDER BY v.fecha_hora_lectura DESC
            LIMIT 15000 
        ) AS sub
        ORDER BY sub.fecha_hora_lectura ASC;
        """
        cursor.execute(sql, (campo_id, fecha_fin, minutos, fecha_fin))
        return cursor.fetchall()

    except Exception as e:
        print(f"❌ [DB Error] ventana_tiempo: {e}")
        raise e
    finally:
        if conn: conn.close()

# -----------------------------------------------------------------------------
# 3. HISTÓRICO (OPTIMIZADO)
# -----------------------------------------------------------------------------
async def obtener_historico_campo_db(
    campo_id: int, fecha_inicio: datetime, fecha_fin: datetime, metodo_carga: str = 'optimizado'
) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        rango_dias = (fecha_fin - fecha_inicio).days
        
        if metodo_carga == 'puro' or rango_dias < 1:
            sql = """
            SELECT * FROM (
                SELECT v.valor, v.fecha_hora_lectura, um.magnitud_tipo, um.simbolo AS simbolo_unidad
                FROM valores v JOIN campos_sensores cs ON v.campo_id = cs.id
                LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
                WHERE v.campo_id = %s AND v.fecha_hora_lectura BETWEEN %s AND %s
                ORDER BY v.fecha_hora_lectura DESC LIMIT 15000 
            ) AS sub ORDER BY sub.fecha_hora_lectura ASC;
            """
            cursor.execute(sql, (campo_id, fecha_inicio, fecha_fin))
            return cursor.fetchall()
        else:
            sql_agregada = """
            SELECT TIMESTAMP(va.fecha, MAKETIME(va.hora, 0, 0)) as fecha_hora_lectura,
                CASE WHEN cs.nombre LIKE '%%Movimiento%%' THEN va.valor_sum ELSE va.valor_avg END as valor,
                um.magnitud_tipo, um.simbolo AS simbolo_unidad
            FROM valores_agregados va JOIN campos_sensores cs ON va.campo_id = cs.id
            LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
            WHERE va.campo_id = %s AND va.fecha BETWEEN %s AND %s
            ORDER BY va.fecha ASC, va.hora ASC;
            """
            cursor.execute(sql_agregada, (campo_id, fecha_inicio.date(), fecha_fin.date()))
            resultados = cursor.fetchall()
            if resultados: return resultados
            
            print(f"⚠️ [DB] Sin datos pre-agregados. Ejecutando agregación AL VUELO.")
            sql_on_the_fly = """
            SELECT 
                DATE_FORMAT(MIN(v.fecha_hora_lectura), '%%Y-%%m-%%d %%H:00:00') as fecha_hora_lectura,
                CASE 
                    WHEN MAX(cs.nombre) LIKE '%%Movimiento%%' THEN SUM(v.valor)
                    ELSE AVG(v.valor) 
                END as valor,
                MAX(um.magnitud_tipo) as magnitud_tipo,
                MAX(um.simbolo) AS simbolo_unidad
            FROM valores v
            JOIN campos_sensores cs ON v.campo_id = cs.id
            LEFT JOIN unidades_medida um ON cs.unidad_medida_id = um.id
            WHERE v.campo_id = %s 
              AND v.fecha_hora_lectura BETWEEN %s AND %s
            GROUP BY DATE(v.fecha_hora_lectura), HOUR(v.fecha_hora_lectura)
            ORDER BY fecha_hora_lectura ASC;
            """
            cursor.execute(sql_on_the_fly, (campo_id, fecha_inicio, fecha_fin))
            return cursor.fetchall()

    except Exception as e:
        print(f"❌ [DB Error] historico: {e}")
        raise e
    finally:
        if conn: conn.close()

# -----------------------------------------------------------------------------
# 4. RANGO DE FECHAS
# -----------------------------------------------------------------------------
async def obtener_rango_fechas_db(dispositivo_id: int) -> Dict[str, Any]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT MIN(va.fecha) as fecha_minima, MAX(va.fecha) as fecha_maxima FROM valores_agregados va JOIN campos_sensores cs ON va.campo_id = cs.id JOIN sensores s ON cs.sensor_id = s.id WHERE s.dispositivo_id = %s"
        cursor.execute(sql, (dispositivo_id,))
        result = cursor.fetchone()
        if not result or not result['fecha_minima']:
            sql_raw = "SELECT MIN(v.fecha_hora_lectura) as fecha_minima, MAX(v.fecha_hora_lectura) as fecha_maxima FROM valores v JOIN campos_sensores cs ON v.campo_id = cs.id JOIN sensores s ON cs.sensor_id = s.id WHERE s.dispositivo_id = %s"
            cursor.execute(sql_raw, (dispositivo_id,))
            result = cursor.fetchone()
        if not result or not result['fecha_minima']:
             hoy = datetime.now().strftime('%Y-%m-%d')
             return {"fecha_minima": hoy, "fecha_maxima": hoy}
        return result
    except Exception as e:
        print(f"❌ [DB Error] rango_fechas: {e}")
        raise e
    finally:
        if conn: conn.close()