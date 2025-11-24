from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
#clase para los proyectos 
# Modelo base (sin ID)
class ProyectoBase(BaseModel):
    nombre: str
    descripcion: str
    tipo_industria: Optional[str] = 'General' # Valor por defecto a nivel de Pydantic
    usuario_id: int

# Modelo para crear p
class ProyectoCrear(ProyectoBase):
    pass
    
# Modelo para actualizar parcialmente
class ProyectoActualizar(BaseModel):
    
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    tipo_industria: Optional[str] = None 

    usuario_id: int 
# 🚨 NUEVO MODELO DE RESPUESTA
class ProyectoConRol(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    tipo_industria: str
    usuario_id: int # ID del dueño original
    mi_rol: str     # 👈 EL CAMPO NUEVO (Ej: "Propietario", "Observador")

    class Config:
        from_attributes = True
# Modelo con ID, para respuestas
class Proyecto(ProyectoBase):
    id: int

    class Config:
        # 🚨 CORRECCIÓN CLAVE: orm_mode ha sido reemplazado por from_attributes
        from_attributes = True
class RespuestaPaginadaProyectos(BaseModel):
    data: List[ProyectoConRol] # La lista de proyectos
    total: int                 # Total de registros encontrados
    page: int                  # Página actual
    limit: int                 # Límite por página
    total_pages: int