# app/servicios/energetico/dependencias.py

import pandas as pd
from fastapi import Depends, HTTPException, status
from typing import Dict, Optional

from app.servicios.energetico.analizador_historico import AnalizadorHistorico
from app.servicios.energetico.predictor_consumo import PredictorConsumo
from app.servicios.energetico.generador_escenarios import GeneradorEscenarios

# 🎯 Importa la función de acceso a datos de PyMySQL
from app.db.crud.recibos_crud import get_all_recibos_by_lotes 

# 🎯 Importa el ID de usuario para la carga inicial del Analizador
from app.servicios.auth_utils import get_current_user_id 

import logging

logger = logging.getLogger(__name__)

# --- Instancias Singleton (por usuario) ---
# Usaremos un diccionario para almacenar una instancia de AnalizadorHistorico por cada user_id
# Esto es esencial porque AnalizadorHistorico ahora carga datos específicos de un usuario
analizador_instances: Dict[int, AnalizadorHistorico] = {}
predictor_instances: Dict[int, PredictorConsumo] = {} # También por usuario
generador_instances: Dict[int, GeneradorEscenarios] = {} # Y el generador

# ----------------------------------------------------
# DEPENDENCIAS DE FASTAPI
# ----------------------------------------------------

async def get_analizador(user_id: int = Depends(get_current_user_id)) -> AnalizadorHistorico:
    """
    Dependencia de FastAPI que provee una instancia (Singleton por usuario) del AnalizadorHistorico.
    Carga los datos de recibos de energía del usuario desde la DB una sola vez.
    """
    if user_id not in analizador_instances:
        logger.info(f"Iniciando instancia Singleton de AnalizadorHistorico para user_id: {user_id}...")
        
        try:
            # Cargar los datos del usuario desde la DB usando PyMySQL
            # Se pasan lotes=None para cargar TODOS los recibos del usuario inicialmente
            datos_db_raw = get_all_recibos_by_lotes(user_id=user_id, lotes=None)
            
            if not datos_db_raw:
                logger.warning(f"No se encontraron recibos de energía para el user_id: {user_id}. Inicializando Analizador con DF vacío.")
                df_completo_usuario = pd.DataFrame()
            else:
                df_completo_usuario = pd.DataFrame(datos_db_raw)
                logger.info(f"✅ [Singleton] {len(df_completo_usuario)} recibos cargados para user_id: {user_id}.")
            
            # Crear la instancia del Analizador con el DataFrame cargado
            analizador_instances[user_id] = AnalizadorHistorico(df_completo=df_completo_usuario)
            
        except Exception as e:
            logger.error(f"❌ [Singleton] Error crítico al cargar datos energéticos para user_id {user_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Fallo al inicializar el servicio de análisis energético: {e}"
            )
            
    return analizador_instances[user_id]


async def get_predictor(user_id: int = Depends(get_current_user_id)) -> PredictorConsumo:
    """
    Dependencia de FastAPI que provee una instancia (Singleton por usuario) del PredictorConsumo.
    """
    if user_id not in predictor_instances:
        logger.info(f"Iniciando instancia Singleton de PredictorConsumo para user_id: {user_id}...")
        predictor_instances[user_id] = PredictorConsumo()
    return predictor_instances[user_id]


async def get_generador_escenarios(
    analizador: AnalizadorHistorico = Depends(get_analizador),
    predictor: PredictorConsumo = Depends(get_predictor),
    user_id: int = Depends(get_current_user_id) # Solo para registro, las sub-dependencias ya lo usan
) -> GeneradorEscenarios:
    """
    Dependencia de FastAPI que provee una instancia (Singleton por usuario) del GeneradorEscenarios.
    Inyecta las instancias de Analizador y Predictor.
    """
    if user_id not in generador_instances:
        logger.info(f"Iniciando instancia Singleton de GeneradorEscenarios para user_id: {user_id}...")
        generador_instances[user_id] = GeneradorEscenarios(analizador=analizador, predictor=predictor)
    return generador_instances[user_id]