import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
import json


class AnalizadorHistorico:
    def __init__(self):
        self.df: pd.DataFrame | None = None
        # self.df = None
        # self._cargar_datos()
    
    def _cargar_datos(self):
        """Cargar y preparar los datos del CSV"""
        try:
            self.df = pd.read_csv(self.ruta_datos)
            
            # Convertir periodo a datetime
            self.df['periodo'] = pd.to_datetime(self.df['periodo'])
            
            # VERIFICAR Y CORREGIR POSIBLES ERRORES EN LOS DATOS
            self._limpiar_datos()
            
            # Ordenar por fecha
            self.df = self.df.sort_values('periodo')
            
            # Calcular métricas derivadas
            self.df['costo_por_kwh'] = self.df['costo_total'] / self.df['consumo_total_kwh']
            self.df['mes'] = self.df['periodo'].dt.month
            self.df['año'] = self.df['periodo'].dt.year
            
            print(f"Datos cargados correctamente: {len(self.df)} registros")
            print(f"Rango de consumo: {self.df['consumo_total_kwh'].min()} - {self.df['consumo_total_kwh'].max()} kWh")
            
        except Exception as e:
            print(f"Error cargando datos: {str(e)}")
            self.df = pd.DataFrame()
    
    def _limpiar_datos(self):
        """Limpiar y corregir posibles errores en los datos"""
        # Verificar si hay valores atípicos evidentes (como 4900 vs 49000)
        consumo_median = self.df['consumo_total_kwh'].median()
        consumo_std = self.df['consumo_total_kwh'].std()
        
        print(f"Consumo mediano: {consumo_median}, Desviación: {consumo_std}")
        
        # Identificar posibles errores de captura (valores muy bajos)
        for idx, row in self.df.iterrows():
            consumo = row['consumo_total_kwh']
            # Si el consumo es menos del 20% de la mediana, podría ser error
            if consumo < consumo_median * 0.2:
                print(f"⚠️  Posible error en {row['periodo']}: consumo={consumo} (mediana={consumo_median})")
                # Podríamos corregirlo multiplicando por 10 si parece error de dígitos
                if consumo < 10000 and consumo > 1000:
                    correccion = consumo * 10
                    print(f"   → Corrigiendo a: {correccion}")
                    self.df.at[idx, 'consumo_total_kwh'] = correccion
    
    def _convertir_a_python(self, obj):
        """Convertir tipos de numpy a tipos nativos de Python para JSON"""
        if pd.isna(obj):
            return None
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, pd.Series):
            return obj.apply(self._convertir_a_python).tolist()
        else:
            return obj
    
    def _datos_cargados(self):
        """Verificar si los datos están cargados correctamente"""
        return self.df is not None and len(self.df) > 0
    
    async def obtener_analisis_basico(self) -> Dict[str, Any]:
        """Análisis descriptivo básico del histórico"""
        if not self._datos_cargados():
            return {"error": "No hay datos disponibles"}
        
        try:
            # USAR MÉTODOS PANDAS DIRECTAMENTE PARA EVITAR PROBLEMAS
            df_temp = self.df.copy()
            
            # Estadísticas básicas - CONVERTIR A PYTHON NATIVO
            consumo_stats = {
                "total_registros": len(df_temp),
                "rango_fechas": {
                    "inicio": df_temp['periodo'].min().strftime('%Y-%m-%d'),
                    "fin": df_temp['periodo'].max().strftime('%Y-%m-%d')
                },
                "consumo_promedio_kwh": float(round(df_temp['consumo_total_kwh'].mean(), 2)),
                "consumo_max_kwh": float(round(df_temp['consumo_total_kwh'].max(), 2)),
                "consumo_min_kwh": float(round(df_temp['consumo_total_kwh'].min(), 2)),
                "costo_promedio_mxn": float(round(df_temp['costo_total'].mean(), 2)),
                "costo_total_acumulado": float(round(df_temp['costo_total'].sum(), 2)),
                "demanda_maxima_promedio_kw": float(round(df_temp['demanda_maxima_kw'].mean(), 2)),
            }
            
            # Añadir factor de potencia solo si existe la columna y tiene valores
            if 'factor_potencia' in df_temp.columns:
                factor_potencia_mean = df_temp['factor_potencia'].mean()
                if not pd.isna(factor_potencia_mean):
                    consumo_stats["factor_potencia_promedio"] = float(round(factor_potencia_mean, 2))
            
            # Tendencias mensuales - MÉTODO MÁS SEGURO
            tendencias = []
            for periodo in df_temp['periodo'].dt.to_period('M').unique():
                mask = df_temp['periodo'].dt.to_period('M') == periodo
                datos_mes = df_temp[mask]
                
                if len(datos_mes) > 0:
                    tendencias.append({
                        'periodo': str(periodo),
                        'consumo_total_kwh': float(round(datos_mes['consumo_total_kwh'].mean(), 2)),
                        'costo_total': float(round(datos_mes['costo_total'].mean(), 2))
                    })
            
            return {
                "estadisticas_basicas": consumo_stats,
                "tendencias_mensuales": tendencias
            }
            
        except Exception as e:
            print(f"Error detallado en análisis: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {"error": f"Error en análisis: {str(e)}"}
    
    async def obtener_estadisticas_detalladas(self) -> Dict[str, Any]:
        """Estadísticas detalladas por año y mes"""
        if not self._datos_cargados():
            return {"error": "No hay datos disponibles"}
        
        try:
            df_temp = self.df.copy()
            
            # Estadísticas por año - MÉTODO MÁS SEGURO
            stats_anuales = []
            for año in df_temp['año'].unique():
                datos_año = df_temp[df_temp['año'] == año]
                stats_anuales.append({
                    'año': int(año),
                    'consumo_total_kwh_sum': float(round(datos_año['consumo_total_kwh'].sum(), 2)),
                    'consumo_total_kwh_mean': float(round(datos_año['consumo_total_kwh'].mean(), 2)),
                    'consumo_total_kwh_std': float(round(datos_año['consumo_total_kwh'].std(), 2)),
                    'costo_total_sum': float(round(datos_año['costo_total'].sum(), 2)),
                    'costo_total_mean': float(round(datos_año['costo_total'].mean(), 2)),
                    'demanda_maxima_kw_max': float(round(datos_año['demanda_maxima_kw'].max(), 2)),
                    'demanda_maxima_kw_mean': float(round(datos_año['demanda_maxima_kw'].mean(), 2)),
                })
            
            # Patrón mensual
            patron_mensual = []
            for mes in range(1, 13):
                datos_mes = df_temp[df_temp['mes'] == mes]
                if len(datos_mes) > 0:
                    patron_mensual.append({
                        'mes': int(mes),
                        'consumo_total_kwh': float(round(datos_mes['consumo_total_kwh'].mean(), 2)),
                        'costo_total': float(round(datos_mes['costo_total'].mean(), 2))
                    })
            
            # Correlaciones
            correlacion_consumo_costo = float(round(df_temp['consumo_total_kwh'].corr(df_temp['costo_total']), 3))
            correlacion_demanda_consumo = float(round(df_temp['demanda_maxima_kw'].corr(df_temp['consumo_total_kwh']), 3))
            
            return {
                "estadisticas_anuales": stats_anuales,
                "patron_mensual": patron_mensual,
                "correlaciones": {
                    "consumo_costo": correlacion_consumo_costo,
                    "demanda_consumo": correlacion_demanda_consumo
                }
            }
            
        except Exception as e:
            print(f"Error detallado en estadísticas: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {"error": f"Error en estadísticas detalladas: {str(e)}"}
    
    async def obtener_muestra_datos(self, limite: int = 10) -> List[Dict]:
        """Obtener muestra de datos para verificación"""
        if not self._datos_cargados():
            return []
        
        try:
            muestra = self.df.head(limite).copy()
            muestra['periodo'] = muestra['periodo'].dt.strftime('%Y-%m-%d')
            
            # Convertir DataFrame a lista de diccionarios con tipos nativos
            resultado = []
            for _, row in muestra.iterrows():
                fila_dict = {}
                for columna, valor in row.items():
                    fila_dict[columna] = self._convertir_a_python(valor)
                resultado.append(fila_dict)
            
            return resultado
        except Exception as e:
            print(f"Error en muestra de datos: {str(e)}")
            return []