# app/api/rutas/recepcion.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any

# Importa el modelo de Pydantic y la función de servicio
from app.api.modelos.recepcion_datos import PayloadDispositivo
from app.servicios.servicio_recepcion import procesar_datos_dispositivo_db

router_recepcion = APIRouter()

@router_recepcion.post("/guardar_json/")
async def recibir_datos_dispositivo(datos: PayloadDispositivo) -> Dict[str, Any]:
    """
    Endpoint de alta velocidad para la ingesta de datos de dispositivos IoT.
    No requiere autenticación JWT de usuario.
    """
    try:
        # Llama a la función de servicio que hace el trabajo pesado
        resultado = await procesar_datos_dispositivo_db(datos)
        return resultado
        
    except HTTPException as e:
        # Si el servicio lanzó una excepción HTTP (ej. 404), la relanza
        raise e
    except Exception as e:
        # Captura cualquier otro error inesperado
        return JSONResponse(
            status_code=500,
            content={"status": "error", "paquete_id": datos.id_paquete, "detail": str(e)}
        )