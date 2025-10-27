from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import pandas as pd
from app.servicios.energetico.analizador_historico import AnalizadorHistorico
from app.servicios.energetico.dependencias import get_analizador
router = APIRouter(prefix="/energetico", tags=["Simulador Energético"])

@router.get("/analisis/historico")
async def analisis_historico(analizador: AnalizadorHistorico = Depends(get_analizador)):
    """Endpoint básico para análisis descriptivo del histórico"""
    try:
       
        if not analizador._datos_cargados():
            raise HTTPException(status_code=503, detail="Datos históricos no disponibles o no pudieron cargarse.")
            
        resultado = await analizador.obtener_analisis_basico()
        return {
            "status": "success",
            "data": resultado,
            "message": "Análisis histórico generado correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")


@router.get("/analisis/estadisticas")
async def estadisticas_detalladas(analizador: AnalizadorHistorico = Depends(get_analizador)):
    """Estadísticas detalladas de consumo y costos"""
    try:
        if not analizador._datos_cargados():
            raise HTTPException(status_code=503, detail="Datos históricos no disponibles.")
        resultado = await analizador.obtener_estadisticas_detalladas()
        return {
            "status": "success", 
            "data": resultado,
            "message": "Estadísticas calculadas correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando estadísticas: {str(e)}")

@router.get("/datos/muestra")
async def obtener_muestra_datos(limite: int = 10, analizador: AnalizadorHistorico = Depends(get_analizador)):
    """Obtener una muestra de los datos para verificación"""
    try:
        if not analizador._datos_cargados():
            raise HTTPException(status_code=503, detail="Datos históricos no disponibles.")
        
        resultado = await analizador.obtener_muestra_datos(limite)
        return {
            "status": "success",
            "data": resultado,
            "message": f"Muestra de {limite} registros obtenida correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo muestra: {str(e)}")