import csv
import datetime
import random
import math
import time

# --- 1. CONFIGURACIÓN DE LA SIMULACIÓN ---
DEVICE_ID = 1
SIMULATION_DAYS = 30
INTERVAL_SECONDS = 5
OUTPUT_FILE = 'simulacion_aula_1mes_corregida.csv'

# --- 2. CONSTANTES DEL AULA (BASADO EN TU INVESTIGACIÓN) ---

# Horarios de clase (Lunes a Viernes)
CLASS_START_M = 7  # 7:00 AM
CLASS_END_M = 14   # 2:00 PM
CLASS_START_V = 14 # 2:00 PM
CLASS_END_V = 22   # 10:00 PM

# Clima Base (Otoño en Chetumal)
TEMP_EXT_MIN = 19.0 # Mínima nocturna
TEMP_EXT_MAX = 30.0 # Máxima diurna
HUM_EXT_MIN = 75.0  # Humedad exterior mínima
HUM_EXT_MAX = 85.0  # Humedad exterior máxima

# Lógica del Aire Acondicionado (A/C)
AC_THRESHOLD_TEMP = 25.0 # Temp. interior para encender el A/C
AC_TARGET_TEMP = 22.0    # Temp. objetivo del A/C
AC_TARGET_HUM = 60.0     # Humedad objetivo del A/C

# Constantes eléctricas MEJORADAS
POWER_BASE_LOAD = 250
POWER_PC_LOAD = 2500
POWER_LIGHTS = 500
POWER_AC_LOAD = 5500
VOLTAGE = 220.0
POWER_FACTOR_BASE = 0.95  # Factor de potencia para carga base
POWER_FACTOR_PC = 0.85    # Factor de potencia para PCs (menos eficiente)
POWER_FACTOR_AC = 0.90    # Factor de potencia para A/C

def simular_clima_exterior(hour_fraction):
    # ... (igual que antes)
    sin_wave = math.sin(math.pi * (hour_fraction - 0.25) * 2) 
    temp_range = (TEMP_EXT_MAX - TEMP_EXT_MIN) / 2
    temp_avg = (TEMP_EXT_MAX + TEMP_EXT_MIN) / 2
    
    # Añade ruido aleatorio
    temp_exterior = temp_avg + temp_range * sin_wave + random.uniform(-0.5, 0.5)
    hum_exterior = random.uniform(HUM_EXT_MIN, HUM_EXT_MAX)
    
    return temp_exterior, hum_exterior

def main():
    print(f"Iniciando simulación CORREGIDA de {SIMULATION_DAYS} días...")
    
    start_time = time.time()
    current_time = datetime.datetime(2025, 10, 1, 0, 0, 0)
    end_time = current_time + datetime.timedelta(days=SIMULATION_DAYS)
    paquete_id = 1
    
    # VARIABLES DE ENERGÍA MEJORADAS
    energia_total_acumulada = 0.0
    energia_dia_actual = 0.0
    dia_actual = current_time.day
    
    # Estado del aula
    temp_interior = 24.0
    hum_interior = 80.0

    # Definir el CSV
    header = [
        'Dispositivo_id', 'Paquete_id', 'Fecha', 'Hora', 
        'Temperatura', 'Humedad', 'Corriente', 'Potencia', 'Energia_Total', 'Energia_Diaria',
        'Iluminacion', 'Movimiento'
    ]
    
    total_rows = 0

    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        while current_time < end_time:
            
            # --- A. Verificar cambio de día (PARA ENERGÍA DIARIA) ---
            if current_time.day != dia_actual:
                energia_dia_actual = 0.0  # Reset energía diaria
                dia_actual = current_time.day
            
            # --- B. Determinar Estado del Aula (igual que antes) ---
            day_of_week = current_time.weekday()
            hour_of_day = current_time.hour
            is_weekend = (day_of_week >= 5)
            is_class_time = (not is_weekend) and \
                            ((CLASS_START_M <= hour_of_day < CLASS_END_M) or \
                             (CLASS_START_V <= hour_of_day < CLASS_END_V))
            
            if is_class_time:
                is_occupied = random.random() < 0.95
            else:
                is_occupied = random.random() < 0.01
            
            # --- C. Simular Clima y A/C (igual que antes) ---
            hour_fraction = (hour_of_day + current_time.minute / 60) / 24.0
            temp_exterior, hum_exterior = simular_clima_exterior(hour_fraction)
            
            is_ac_on = is_occupied and temp_interior > AC_THRESHOLD_TEMP
            
            if is_ac_on:
                temp_interior += (AC_TARGET_TEMP - temp_interior) * 0.1 + random.uniform(-0.1, 0.1)
                hum_interior += (AC_TARGET_HUM - hum_interior) * 0.1 + random.uniform(-0.2, 0.2)
            else:
                temp_interior += (temp_exterior - temp_interior) * 0.01 + random.uniform(-0.1, 0.1)
                hum_interior += (hum_exterior - hum_interior) * 0.01 + random.uniform(-0.2, 0.2)
            
            hum_interior = max(40.0, min(99.9, hum_interior))

            # --- D. SIMULACIÓN ELÉCTRICA MEJORADA ---
            potencia_activa = POWER_BASE_LOAD
            factor_potencia = POWER_FACTOR_BASE
            
            if is_occupied:
                potencia_activa += POWER_PC_LOAD + random.uniform(-200, 200)
                factor_potencia = POWER_FACTOR_PC  # Los PCs tienen peor factor de potencia
            
            if is_occupied:  # Luces solo cuando está ocupado
                potencia_activa += POWER_LIGHTS
            
            if is_ac_on:
                potencia_activa += POWER_AC_LOAD + random.uniform(-100, 100)
                factor_potencia = POWER_FACTOR_AC  # A/C tiene su propio factor

            # CÁLCULO DE CORRIENTE MEJORADO (considera factor de potencia)
            potencia_aparente = potencia_activa / factor_potencia
            corriente = potencia_aparente / VOLTAGE

            # CÁLCULO DE ENERGÍA MEJORADO
            incremento_energia = (potencia_activa / 1000.0) * (INTERVAL_SECONDS / 3600.0)
            energia_total_acumulada += incremento_energia
            energia_dia_actual += incremento_energia

            # --- E. Sensores de Ocupación (igual que antes) ---
            movimiento = 1 if is_occupied and random.random() < 0.8 else 0
            
            if is_occupied:
                iluminacion = random.uniform(450, 600)
            elif 7 <= hour_of_day < 18:
                iluminacion = random.uniform(100, 250)
            else:
                iluminacion = random.uniform(0, 10)

            # --- F. Escribir Fila ---
            fecha_str = current_time.strftime('%Y-%m-%d')
            hora_str = current_time.strftime('%H:%M:%S')
            
            writer.writerow([
                DEVICE_ID, paquete_id, fecha_str, hora_str,
                round(temp_interior, 2),
                round(hum_interior, 2),
                round(corriente, 6),  # Más decimales para corriente realista
                round(potencia_activa, 2),
                round(energia_total_acumulada, 6),  # Energía total acumulada
                round(energia_dia_actual, 6),       # Energía del día actual
                round(iluminacion, 0),
                movimiento
            ])
            
            # --- G. Incrementar Tiempo ---
            current_time += datetime.timedelta(seconds=INTERVAL_SECONDS)
            paquete_id += 1
            total_rows += 1
            
            if total_rows % 100000 == 0:
                print(f"  ... {total_rows:,} registros generados ...")
                # Mostrar ejemplo de datos para verificar coherencia
                print(f"    Ejemplo - Potencia: {potencia_activa:.2f}W, Corriente: {corriente:.4f}A, Energía_Diaria: {energia_dia_actual:.4f}kWh")

    end_gen_time = time.time()
    print("-" * 50)
    print("SIMULACIÓN CORREGIDA COMPLETADA")
    print(f"Total registros: {total_rows:,}")
    print(f"Energía total simulada: {energia_total_acumulada:.2f} kWh")
    print(f"Tiempo: {end_gen_time - start_time:.2f} segundos")
    print(f"Archivo: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()