from pydantic import BaseModel
from typing import List, Dict, Optional, Any
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

# Modelo con ID, para respuestas
class Proyecto(ProyectoBase):
    id: int

    class Config:
        # 🚨 CORRECCIÓN CLAVE: orm_mode ha sido reemplazado por from_attributes
        from_attributes = True