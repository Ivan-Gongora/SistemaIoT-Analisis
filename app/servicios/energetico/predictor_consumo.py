import pandas as pd
import numpy as np
from prophet import Prophet
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from app.configuracion import ConfigEnergetico

logger = logging.getLogger(__name__)

class PredictorConsumo:
    def __init__(self):
        self.modelo = None
        self.df_entrenado = None
    
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
        
    async def entrenar_modelo_prophet(self, df: pd.DataFrame) -> bool:
        """Entrenar modelo Prophet con datos históricos"""
        try:
            # Preparar datos para Prophet
            df_prophet = df[['periodo', 'consumo_total_kwh']].copy()
            df_prophet.columns = ['ds', 'y']
            df_prophet = df_prophet.sort_values('ds')
            
            # Crear y entrenar modelo
            self.modelo = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,  # No tenemos datos semanales
                daily_seasonality=False,   # No tenemos datos diarios
                changepoint_prior_scale=0.05,
                seasonality_prior_scale=10.0
            )
            
            # Añadir estacionalidad mensual personalizada
            self.modelo.add_seasonality(
                name='monthly', 
                period=30.5, 
                fourier_order=5
            )
            
            self.modelo.fit(df_prophet)
            self.df_entrenado = df_prophet
            
            logger.info(f"Modelo Prophet entrenado con {len(df_prophet)} registros")
            return True
            
        except Exception as e:
            logger.error(f"Error entrenando modelo: {str(e)}")
            return False
    
    async def predecir_consumo(self, meses: int = 12) -> Dict[str, Any]:
        """Predecir consumo para los próximos meses"""
        if self.modelo is None:
            return {"error": "Modelo no entrenado"}
        
        try:
            # Crear dataframe futuro
            futuro = self.modelo.make_future_dataframe(
                periods=meses, 
                freq='M',  # Mensual
                include_history=False
            )
            
            # Hacer predicción
            forecast = self.modelo.predict(futuro)
            
            # Preparar resultados CONVERSION A PYTHON NATIVO
            predicciones = []
            for _, row in forecast.iterrows():
                predicciones.append({
                    'periodo': self._convertir_a_python(row['ds'].strftime('%Y-%m-%d')),
                    'consumo_predicho_kwh': self._convertir_a_python(max(0, round(row['yhat'], 2))),
                    'limite_inferior': self._convertir_a_python(max(0, round(row['yhat_lower'], 2))),
                    'limite_superior': self._convertir_a_python(max(0, round(row['yhat_upper'], 2))),
                    'tendencia': self._convertir_a_python(round(row['trend'], 2))
                })
            
            # Calcular métricas de confianza CONVERSION A PYTHON NATIVO
            ultimo_real = self.df_entrenado['y'].iloc[-1] if len(self.df_entrenado) > 0 else 0
            primera_prediccion = predicciones[0]['consumo_predicho_kwh'] if predicciones else 0
            
            return {
                "predicciones": predicciones,
                "metricas_modelo": {
                    "registros_entrenamiento": self._convertir_a_python(len(self.df_entrenado)),
                    "ultimo_valor_real": self._convertir_a_python(ultimo_real),
                    "primera_prediccion": self._convertir_a_python(primera_prediccion),
                    "cambio_porcentual": self._convertir_a_python(round(((primera_prediccion - ultimo_real) / ultimo_real * 100), 2) if ultimo_real > 0 else 0),
                    "horizonte_prediccion": self._convertir_a_python(meses)
                }
            }
            
        except Exception as e:
            logger.error(f"Error en predicción: {str(e)}")
            return {"error": f"Error en predicción: {str(e)}"}
    
    async def predecir_costo(self, df_historico: pd.DataFrame, meses: int = 12) -> Dict[str, Any]:
        """Predecir costos basado en la relación consumo-costo"""
        try:
            # Calcular relación histórica consumo-costo
            df_historico['relacion_costo_consumo'] = df_historico['costo_total'] / df_historico['consumo_total_kwh']
            relacion_promedio = df_historico['relacion_costo_consumo'].mean()
            
            # Obtener predicciones de consumo
            resultado_consumo = await self.predecir_consumo(meses)
            
            if 'error' in resultado_consumo:
                return resultado_consumo
            
            # Calcular costos predichos CONVERSION A PYTHON NATIVO
            predicciones_costo = []
            for pred in resultado_consumo['predicciones']:
                costo_predicho = pred['consumo_predicho_kwh'] * relacion_promedio
                predicciones_costo.append({
                    'periodo': pred['periodo'],
                    'costo_predicho_mxn': self._convertir_a_python(round(costo_predicho, 2)),
                    'consumo_predicho_kwh': pred['consumo_predicho_kwh'],
                    'costo_por_kwh_predicho': self._convertir_a_python(round(relacion_promedio, 4))
                })
            
            return {
                "predicciones_costo": predicciones_costo,
                "relacion_promedio_consumo_costo": self._convertir_a_python(round(relacion_promedio, 4)),
                "based_on_consumo_predicciones": True
            }
            
        except Exception as e:
            logger.error(f"Error prediciendo costos: {str(e)}")
            return {"error": f"Error prediciendo costos: {str(e)}"}
        
    async def predecir_tendencia_lineal(self, df: pd.DataFrame, meses: int = 12) -> Dict[str, Any]:
        """Predicción simple basada en tendencia lineal - mejor para pocos datos"""
        try:
            # Preparar datos
            df_temp = df[['periodo', 'consumo_total_kwh']].copy()
            df_temp = df_temp.sort_values('periodo')
            
            # Crear variable temporal (meses desde inicio)
            df_temp['mes_num'] = range(len(df_temp))
            
            # Modelo de regresión lineal simple
            from sklearn.linear_model import LinearRegression
            X = df_temp[['mes_num']].values
            y = df_temp['consumo_total_kwh'].values
            
            modelo = LinearRegression()
            modelo.fit(X, y)
            
            # Predecir próximos meses
            ultimo_mes = df_temp['mes_num'].max()
            meses_futuros = np.array([[ultimo_mes + i + 1] for i in range(meses)])
            predicciones = modelo.predict(meses_futuros)
            
            # Calcular intervalo de confianza simple
            residuos = y - modelo.predict(X)
            std_error = residuos.std()
            
            # Generar resultados
            predicciones_lista = []
            fecha_base = df_temp['periodo'].max()
            
            for i, pred in enumerate(predicciones):
                # Calcular fecha (aproximadamente 30 días por mes)
                fecha_pred = fecha_base + pd.DateOffset(months=i+1)
                
                predicciones_lista.append({
                    'periodo': self._convertir_a_python(fecha_pred.strftime('%Y-%m-%d')),
                    'consumo_predicho_kwh': self._convertir_a_python(max(0, round(float(pred), 2))),
                    'limite_inferior': self._convertir_a_python(max(0, round(float(pred - 1.96 * std_error), 2))),
                    'limite_superior': self._convertir_a_python(max(0, round(float(pred + 1.96 * std_error), 2))),
                    'tendencia': self._convertir_a_python(round(float(pred), 2))
                })
            
            # Métricas
            ultimo_real = float(y[-1])
            primera_prediccion = float(predicciones[0])
            
            return {
                "predicciones": predicciones_lista,
                "metricas_modelo": {
                    "registros_entrenamiento": self._convertir_a_python(len(df_temp)),
                    "ultimo_valor_real": self._convertir_a_python(ultimo_real),
                    "primera_prediccion": self._convertir_a_python(primera_prediccion),
                    "cambio_porcentual": self._convertir_a_python(round(((primera_prediccion - ultimo_real) / ultimo_real * 100), 2)),
                    "horizonte_prediccion": self._convertir_a_python(meses),
                    "tipo_modelo": "regresion_lineal",
                    "r2_score": self._convertir_a_python(round(modelo.score(X, y), 4)),
                    "pendiente": self._convertir_a_python(round(modelo.coef_[0], 2))
                }
            }
            
        except Exception as e:
            logger.error(f"Error en tendencia lineal: {str(e)}")
            return {"error": f"Error en tendencia lineal: {str(e)}"}