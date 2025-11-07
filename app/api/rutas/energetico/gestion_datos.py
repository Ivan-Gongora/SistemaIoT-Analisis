# app/api/rutas/energetico/gestion_datos.py (MODIFICACIÓN)

import pymysql
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
import logging

from app.servicios.auth_utils import get_current_user_id 
# 🎯 Importar la nueva función de servicio
from app.servicios.energetico.gestion_datos_servicio import procesar_y_guardar_csv_recibos

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/energetico", tags=["Gestión de Datos Energéticos"])

@router.post("/cargar-csv", 
             status_code=status.HTTP_201_CREATED,
             summary="Cargar datos de recibos desde un CSV (Protegido)")
async def cargar_datos_csv(
    file: UploadFile = File(..., description="Archivo CSV con los datos de recibos"),
    lote_nombre: str = Form(..., description="Nombre identificador para este conjunto de datos (ej. 'Recibos Casa 2023')"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Sube un archivo CSV con datos históricos de recibos de energía,
    los valida y los almacena en la tabla 'recibos_energia'.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser de tipo CSV.")
        
    try:
        contents = await file.read()
        
        num_registros = await procesar_y_guardar_csv_recibos(
            file_contents=contents,
            lote_nombre=lote_nombre,
            user_id=current_user_id
        )

        return {"message": f"Datos cargados exitosamente al lote '{lote_nombre}': {num_registros} registros insertados."}

    except ValueError as ve:
        # Errores de validación de datos (columnas, Pydantic, nombre de lote)
        logger.error(f"[{current_user_id}] Error de validación al cargar CSV: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    
    except pymysql.err.IntegrityError as ie:
        # Errores específicos de la base de datos (ej. duplicados)
        logger.warning(f"[{current_user_id}] Error de integridad DB al cargar CSV: {ie}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ie))
        
    except Exception as e:
        # Cualquier otro error inesperado
        import traceback
        logger.error(f"[{current_user_id}] Error inesperado al cargar CSV: {traceback.format_exc()}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")