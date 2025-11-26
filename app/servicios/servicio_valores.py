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
#  MOTOR DE ANÁLISIS 1: INDIVIDUAL (INTELIGENTE)
# -----------------------------------------------------------------------------
async def detectar_anomalia_individual(campo_id: int, valor_actual: float) -> tuple[bool, Optional[str]]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1. Obtener contexto histórico + METADATOS (Tipo de dato)
        sql = """
        SELECT v.valor, cs.nombre, cs.tipo_valor
        FROM valores v 
        JOIN campos_sensores cs ON v.campo_id = cs.id
        WHERE v.campo_id = %s 
        ORDER BY v.fecha_hora_lectura DESC 
        LIMIT 60
        """
        cursor.execute(sql, (campo_id,))
        rows = cursor.fetchall()
        
        if not rows or len(rows) < 10:
            return False, None 

        # Detectar Tipo de Sensor
        tipo = (rows[0].get('tipo_valor') or '').lower()
        nombre = (rows[0].get('nombre') or '').lower()
        es_movimiento = 'bool' in tipo or 'movimiento' in nombre or 'estado' in nombre

        # --- RAMA A: ANÁLISIS DE MOVIMIENTO (FRECUENCIA) ---
        if es_movimiento:
            # Calcular "Densidad de Movimiento" reciente
            # Tomamos los últimos 10 registros (aprox 1 minuto si es cada 5s)
            ventana_reciente = rows[:10]
            suma_reciente = sum(float(r['valor']) for r in ventana_reciente)
            
            # Historia previa (para comparar)
            historia_previa = rows[10:]
            if not historia_previa: return False, None
            
            # Promedio de actividad en bloques de 10
            bloques = [historia_previa[i:i + 10] for i in range(0, len(historia_previa), 10)]
            promedios_bloques = []
            for bloque in bloques:
                suma = sum(float(r['valor']) for r in bloque)
                promedios_bloques.append(suma)
            
            media_actividad = sum(promedios_bloques) / len(promedios_bloques) if promedios_bloques else 0
            
            # Umbral: Si la actividad actual es el TRIPLE del promedio normal
            if suma_reciente > (media_actividad * 3) and suma_reciente > 2:
                return True, f"Alta Actividad ({int(suma_reciente)} eventos recientes)"
            
            return False, None

        # --- RAMA B: ANÁLISIS NUMÉRICO (Z-SCORE SUAVIZADO) ---
        else:
            historial = [float(r['valor']) for r in rows]
            
            ventana_reciente = historial[:3] 
            valor_suavizado = sum(ventana_reciente) / len(ventana_reciente)
            
            linea_base = historial[3:]
            media_base = sum(linea_base) / len(linea_base)
            varianza = sum([((x - media_base) ** 2) for x in linea_base]) / len(linea_base)
            desviacion = math.sqrt(varianza)

            if desviacion < 0.1: desviacion = 0.1

            z_score = (valor_suavizado - media_base) / desviacion
            UMBRAL = 3.0 

            if abs(z_score) > UMBRAL:
                tipo = "Crítico Alto" if z_score > 0 else "Crítico Bajo"
                return True, f"{tipo} detectado ({valor_suavizado:.1f})"
            
            return False, None

    except Exception as e:
        print(f"⚠️ Error análisis realtime: {e}")
        return False, None
    finally:
        if conn: conn.close()

# -----------------------------------------------------------------------------
#  MOTOR DE ANÁLISIS 2: POR LOTES
# -----------------------------------------------------------------------------
def aplicar_analisis_anomalias(datos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not datos or len(datos) < 10: return datos

    # Detectar tipo basado en el primer registro (asumiendo homogeneidad)
    es_movimiento = False
    if datos[0].get('nombre_campo'):
        nombre = datos[0]['nombre_campo'].lower()
        es_movimiento = 'movimiento' in nombre or 'estado' in nombre

    if es_movimiento:
        # Lógica simple para lotes de movimiento:
        # Marcar si el valor acumulado (si es barra) es muy alto
        valores = [float(d['valor']) for d in datos]
        max_val = max(valores)
        media = sum(valores) / len(valores)
        
        for d in datos:
            val = float(d['valor'])
            # Si es un pico muy alto respecto al promedio (3x)
            if val > (media * 3) and val > 5: 
                d['anomalia'] = True
                d['mensaje_alerta'] = f"Pico de Actividad ({int(val)} eventos)"
            else:
                d['anomalia'] = False
                d['mensaje_alerta'] = None
    else:
        # Lógica Z-Score estándar
        valores = [float(d['valor']) for d in datos]
        media = sum(valores) / len(valores)
        varianza = sum([((x - media) ** 2) for x in valores]) / len(valores)
        desviacion_std = math.sqrt(varianza)
        if desviacion_std < 0.01: desviacion_std = 0.01
        UMBRAL_Z = 2.8 

        for d in datos:
            val = float(d['valor'])
            z_score = (val - media) / desviacion_std
            if abs(z_score) > UMBRAL_Z:
                d['anomalia'] = True
                d['mensaje_alerta'] = f"Valor atípico: {val}"
            else:
                d['anomalia'] = False
                d['mensaje_alerta'] = None
    
    return datos

# -----------------------------------------------------------------------------
# 2. VENTANA DE TIEMPO
# -----------------------------------------------------------------------------
async def obtener_valores_ventana_db(campo_id: int, minutos: int) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # PASO 1: Obtener ancla
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
                um.simbolo AS simbolo_unidad
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
# 3. HISTÓRICO (OPTIMIZADO CON FALLBACK)
# -----------------------------------------------------------------------------
async def obtener_historico_campo_db(
    campo_id: int, fecha_inicio: datetime, fecha_fin: datetime, metodo_carga: str = 'optimizado'
) -> List[Dict[str, Any]]:
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        rango_dias = (fecha_fin - fecha_inicio).days
        
        # Caso A: Carga Pura
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
            
        # Caso B: Carga Agregada
        else:
            # Intento 1: Tabla Pre-calculada
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
            
            # Intento 2: Cálculo al Vuelo (Fallback)
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
        
        sql = """
        SELECT MIN(va.fecha) as fecha_minima, MAX(va.fecha) as fecha_maxima
        FROM valores_agregados va
        JOIN campos_sensores cs ON va.campo_id = cs.id
        JOIN sensores s ON cs.sensor_id = s.id
        WHERE s.dispositivo_id = %s
        """
        cursor.execute(sql, (dispositivo_id,))
        result = cursor.fetchone()
        
        if not result or not result['fecha_minima']:
            sql_raw = """
            SELECT MIN(v.fecha_hora_lectura) as fecha_minima, MAX(v.fecha_hora_lectura) as fecha_maxima
            FROM valores v JOIN campos_sensores cs ON v.campo_id = cs.id
            JOIN sensores s ON cs.sensor_id = s.id WHERE s.dispositivo_id = %s
            """
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