from fastapi import APIRouter, HTTPException, Query,Body
from typing import Dict, Any

from app.servicios.energetico.analizador_historico import AnalizadorHistorico
from app.servicios.energetico.predictor_consumo import PredictorConsumo

router = APIRouter(prefix="/energetico", tags=["Predicciones Energéticas"])

@router.get("/optimizacion/recomendaciones")
async def obtener_recomendaciones_optimizacion():
    """Obtener recomendaciones de optimización energética personalizadas"""
    try:
        from app.servicios.energetico.recomendador_optimizacion import RecomendadorOptimizacion
        
        recomendador = RecomendadorOptimizacion()
        resultado = await recomendador.generar_recomendaciones_completas()
        
        return {
            "status": "success",
            "data": resultado,
            "message": "Recomendaciones de optimización generadas correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando recomendaciones: {str(e)}")

@router.get("/proyecciones/mejorada")
async def proyeccion_mejorada(
    meses: int = Query(6, description="Meses a predecir", ge=1, le=24)
):
    """Proyección mejorada que usa el mejor modelo disponible"""
    try:
        analizador = AnalizadorHistorico()
        if not analizador._datos_cargados():
            raise HTTPException(status_code=400, detail="No hay datos históricos disponibles")
        
        predictor = PredictorConsumo()
        
        # Si tenemos pocos datos, usar tendencia lineal (más preciso)
        if len(analizador.df) < 18:  # Menos de 1.5 años
            resultado = await predictor.predecir_tendencia_lineal(analizador.df, meses)
            modelo_usado = "tendencia_lineal"
        else:
            # Si tenemos suficientes datos, usar Prophet
            entrenado = await predictor.entrenar_modelo_prophet(analizador.df)
            if entrenado:
                resultado = await predictor.predecir_consumo(meses)
                modelo_usado = "prophet"
            else:
                resultado = await predictor.predecir_tendencia_lineal(analizador.df, meses)
                modelo_usado = "tendencia_lineal_fallback"
        
        # Añadir información del modelo usado
        if 'error' not in resultado:
            resultado['modelo_usado'] = modelo_usado
        
        return {
            "status": "success",
            "data": resultado,
            "message": f"Proyección mejorada ({modelo_usado}) para {meses} meses generada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en proyección mejorada: {str(e)}")
    
@router.get("/proyecciones/consumo")
async def proyeccion_consumo(
    meses: int = Query(12, description="Meses a predecir", ge=1, le=36)
):
    """Proyección de consumo energético para los próximos meses"""
    try:
        # Obtener datos históricos
        analizador = AnalizadorHistorico()
        if not analizador._datos_cargados():
            raise HTTPException(status_code=400, detail="No hay datos históricos disponibles")
        
        # Entrenar modelo y predecir
        predictor = PredictorConsumo()
        entrenado = await predictor.entrenar_modelo_prophet(analizador.df)
        
        if not entrenado:
            raise HTTPException(status_code=500, detail="Error entrenando modelo predictivo")
        
        resultado = await predictor.predecir_consumo(meses)
        
        return {
            "status": "success",
            "data": resultado,
            "message": f"Proyección de consumo para {meses} meses generada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en proyección: {str(e)}")

@router.get("/proyecciones/costo")
async def proyeccion_costo(
    meses: int = Query(12, description="Meses a predecir", ge=1, le=36)
):
    """Proyección de costos energéticos para los próximos meses"""
    try:
        # Obtener datos históricos
        analizador = AnalizadorHistorico()
        if not analizador._datos_cargados():
            raise HTTPException(status_code=400, detail="No hay datos históricos disponibles")
        
        # Entrenar modelo y predecir costos
        predictor = PredictorConsumo()
        entrenado = await predictor.entrenar_modelo_prophet(analizador.df)
        
        if not entrenado:
            raise HTTPException(status_code=500, detail="Error entrenando modelo predictivo")
        
        resultado = await predictor.predecir_costo(analizador.df, meses)
        
        return {
            "status": "success",
            "data": resultado,
            "message": f"Proyección de costos para {meses} meses generada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en proyección de costos: {str(e)}")

@router.get("/proyecciones/completa")
async def proyeccion_completa(
    meses: int = Query(12, description="Meses a predecir", ge=1, le=36)
):
    """Proyección completa (consumo + costo) para los próximos meses"""
    try:
        analizador = AnalizadorHistorico()
        if not analizador._datos_cargados():
            raise HTTPException(status_code=400, detail="No hay datos históricos disponibles")
        
        predictor = PredictorConsumo()
        entrenado = await predictor.entrenar_modelo_prophet(analizador.df)
        
        if not entrenado:
            raise HTTPException(status_code=500, detail="Error entrenando modelo predictivo")
        
        # Obtener ambas proyecciones
        consumo_result = await predictor.predecir_consumo(meses)
        costo_result = await predictor.predecir_costo(analizador.df, meses)
        
        return {
            "status": "success",
            "data": {
                "proyeccion_consumo": consumo_result,
                "proyeccion_costo": costo_result,
                "resumen": {
                    "meses_predichos": meses,
                    "ultimo_periodo_historico": analizador.df['periodo'].max().strftime('%Y-%m-%d'),
                    "total_registros_entrenamiento": len(analizador.df)
                }
            },
            "message": f"Proyección completa para {meses} meses generada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en proyección completa: {str(e)}")

# Asegúrate de que estén registrados estos endpoints
@router.post("/ia/analisis-avanzado")
async def analisis_avanzado_ia(pregunta: str = Body(..., description="Pregunta específica para análisis IA")):
    """Análisis avanzado con IA de los datos energéticos"""
    try:
        from app.servicios.ia.deepseek_client import DeepSeekClient
        from app.servicios.energetico.analizador_historico import AnalizadorHistorico
        
        analizador = AnalizadorHistorico()
        if not analizador._datos_cargados():
            raise HTTPException(status_code=400, detail="No hay datos disponibles")
        
        # Preparar contexto con datos reales
        stats = await analizador.obtener_analisis_basico()
        estadisticas = stats.get("estadisticas_basicas", {})
        
        contexto = f"""
        RESUMEN ENERGÉTICO INSTITUCIONAL:
        - Período: {estadisticas.get('rango_fechas', {}).get('inicio', '')} a {estadisticas.get('rango_fechas', {}).get('fin', '')}
        - Consumo promedio: {estadisticas.get('consumo_promedio_kwh', 0):,.0f} kWh/mes
        - Costo promedio: ${estadisticas.get('costo_promedio_mxn', 0):,.0f} MXN/mes
        - Demanda máxima: {estadisticas.get('demanda_maxima_promedio_kw', 0):,.0f} kW
        - Total registros: {estadisticas.get('total_registros', 0)} meses
        - Tarifa: GDMTH
        """
        
        cliente_ia = DeepSeekClient()
        respuesta = await cliente_ia.consultar_ia(pregunta, contexto)
        
        return {
            "status": "success",
            "data": {
                "pregunta": pregunta,
                "respuesta_ia": respuesta,
                "contexto_usado": contexto.strip()
            },
            "message": "Análisis IA generado correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis IA: {str(e)}")

@router.get("/ia/analisis-automatico")
async def analisis_automatico_ia():
    """Análisis automático de los datos energéticos por IA"""
    try:
        from app.servicios.ia.deepseek_client import DeepSeekClient
        from app.servicios.energetico.analizador_historico import AnalizadorHistorico
        
        analizador = AnalizadorHistorico()
        if not analizador._datos_cargados():
            raise HTTPException(status_code=400, detail="No hay datos disponibles")
        
        # Preparar resumen detallado
        stats = await analizador.obtener_analisis_basico()
        estadisticas = stats.get("estadisticas_basicas", {})
        
        df_summary = f"""
        DATOS ENERGÉTICOS DETALLADOS:
        - Período: {estadisticas.get('rango_fechas', {}).get('inicio', '')} a {estadisticas.get('rango_fechas', {}).get('fin', '')}
        - Consumo promedio: {estadisticas.get('consumo_promedio_kwh', 0):,.0f} kWh/mes
        - Costo promedio: ${estadisticas.get('costo_promedio_mxn', 0):,.0f} MXN/mes
        - Demanda máxima: {estadisticas.get('demanda_maxima_promedio_kw', 0):,.0f} kW
        - Consumo máximo: {estadisticas.get('consumo_max_kwh', 0):,.0f} kWh
        - Consumo mínimo: {estadisticas.get('consumo_min_kwh', 0):,.0f} kWh
        - Total acumulado: ${estadisticas.get('costo_total_acumulado', 0):,.0f} MXN
        """
        
        cliente_ia = DeepSeekClient()
        respuesta = await cliente_ia.analizar_datos_energeticos(df_summary)
        
        return {
            "status": "success",
            "data": {
                "analisis_automatico": respuesta,
                "resumen_datos": estadisticas
            },
            "message": "Análisis automático IA generado correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis automático IA: {str(e)}")