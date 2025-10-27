import pandas as pd
from app.servicios.energetico.analizador_historico import AnalizadorHistorico
from app.configuracion import ConfigEnergetico  # Asumo que RUTA_RECIBOS está aquí
import logging

logger = logging.getLogger(__name__)

# 1. Variable global para almacenar la instancia única
analizador_global: AnalizadorHistorico | None = None

def cargar_y_procesar_datos_csv() -> pd.DataFrame:
    """
    Función aislada para cargar y pre-procesar el CSV.
    Se ejecuta UNA SOLA VEZ.
    """
    try:
        # Carga los datos (asumiendo la ruta desde tu config)
        df = pd.read_csv(ConfigEnergetico.RUTA_RECIBOS)
        
        # ----------------------------------------------------
        # Mover la lógica de _cargar_datos y _limpiar_datos aquí
        # ----------------------------------------------------
        
        df['periodo'] = pd.to_datetime(df['periodo'])
        df = df.sort_values('periodo')
        
        # Lógica de limpieza
        consumo_median = df['consumo_total_kwh'].median()
        for idx, row in df.iterrows():
            consumo = row['consumo_total_kwh']
            if consumo < consumo_median * 0.2:
                # Corregir error de dígitos (ej. 4900 vs 49000)
                if consumo < 10000 and consumo > 1000:
                    correccion = consumo * 10
                    logger.warning(f"Posible error en {row['periodo']}: {consumo} -> {correccion}")
                    df.at[idx, 'consumo_total_kwh'] = correccion

        # Calcular métricas derivadas
        df['costo_por_kwh'] = df['costo_total'] / df['consumo_total_kwh']
        df['mes'] = df['periodo'].dt.month
        df['año'] = df['periodo'].dt.year
        
        logger.info(f"✅ [Singleton] Datos energéticos cargados y procesados. {len(df)} registros.")
        return df
    
    except Exception as e:
        logger.error(f"❌ [Singleton] Error crítico al cargar datos energéticos: {e}")
        # Devolver un DataFrame vacío en caso de error
        return pd.DataFrame()

# ----------------------------------------------------
# LA DEPENDENCIA DE FASTAPI
# ----------------------------------------------------

def get_analizador() -> AnalizadorHistorico:
    """
    Dependencia de FastAPI que provee el Singleton del Analizador.
    """
    global analizador_global
    
    # Si es la primera vez que se llama, crea la instancia
    if analizador_global is None:
        logger.info("Iniciando instancia Singleton de AnalizadorHistorico...")
        
        # 1. Carga los datos UNA SOLA VEZ
        df_cargado = cargar_y_procesar_datos_csv()
        
        # 2. Crea la instancia y le "inyecta" el DataFrame ya procesado
        analizador_global = AnalizadorHistorico()
        analizador_global.df = df_cargado
    
    # 3. Devuelve la instancia global (ya sea nueva o existente)
    return analizador_global