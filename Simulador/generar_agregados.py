import pymysql
import time

# -----------------------------------------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# -----------------------------------------------------------
# Asegúrate de que coincida con tu base de datos en XAMPP
DB_CONFIG = {
    'host': 'localhost',
    'user': 'sistemaiot',      # El usuario que creaste en tu SQL
    'password': 'raspberry',  # La contraseña que definiste
    'database': 'sistemaiotA_db', # El nombre de tu base de datos
    'port': 3306
}

def conectar_db():
    """Establece conexión con la base de datos MySQL."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("Conexión a MySQL (XAMPP) exitosa.")
        return conn
    except pymysql.Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def ejecutar_agregacion(conn):
    """
    Lee la tabla 'valores', calcula los agregados por hora
    y los inserta en 'valores_agregados'.
    """
    
    # Esta consulta SQL hace todo el trabajo pesado:
    # 1. Selecciona los datos de 'valores'.
    # 2. Agrupa por campo_id, fecha y hora.
    # 3. Calcula MIN, MAX, AVG, y COUNT.
    # 4. Inserta los resultados en 'valores_agregados'.
    # 5. ON DUPLICATE KEY UPDATE: Si el script se ejecuta de nuevo,
    #    actualiza los registros en lugar de fallar.
    
    sql_aggregate = """
    INSERT INTO valores_agregados 
        (campo_id, fecha, hora, valor_min, valor_max, valor_avg, total_registros)
    SELECT
        campo_id,
        DATE(fecha_hora_lectura) AS fecha,
        HOUR(fecha_hora_lectura) AS hora,
        MIN(valor) AS valor_min,
        MAX(valor) AS valor_max,
        AVG(valor) AS valor_avg,
        COUNT(*) AS total_registros
    FROM
        valores
    GROUP BY
        campo_id, fecha, hora
    ON DUPLICATE KEY UPDATE
        valor_min = VALUES(valor_min),
        valor_max = VALUES(valor_max),
        valor_avg = VALUES(valor_avg),
        total_registros = VALUES(total_registros);
    """
    
    try:
        with conn.cursor() as cursor:
            print("Vaciando resúmenes anteriores (TRUNCATE)...")
            # Vaciamos la tabla para asegurar datos limpios en esta prueba
            cursor.execute("TRUNCATE TABLE valores_agregados;") 
            
            print("Ejecutando agregación (leyendo 'valores' y escribiendo en 'valores_agregados')...")
            print("Esto puede tardar unos segundos...")
            start_time = time.time()
            
            # Ejecutar la consulta de agregación principal
            affected_rows = cursor.execute(sql_aggregate)
            
            conn.commit()
            end_time = time.time()
            
            print("\n" + "="*30)
            print("Agregación completada.")
            print(f"Tiempo de procesamiento de agregados: {end_time - start_time:.2f} segundos.")
            print(f"Total de registros de resumen (por hora) generados: {affected_rows}")
            
    except pymysql.Error as e:
        print(f"Error durante la agregación SQL: {e}")
        conn.rollback()

def main():
    conn = conectar_db()
    if conn:
        try:
            ejecutar_agregacion(conn)
        finally:
            conn.close()
            print("Conexión a MySQL cerrada.")

# --- Ejecutar el script ---
if __name__ == "__main__":
    main()