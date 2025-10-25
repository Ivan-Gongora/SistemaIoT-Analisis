from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Modelo base (común a crear y respuesta)
class ValorBase(BaseModel):
    campo_id: int
    valor: float
    fecha_hora_lectura: datetime
    magnitud_tipo: str
# Para crear un nuevo valor (sin ID)
class ValorCrear(ValorBase):
    pass
# Modelo de Respuesta (lo que la API devuelve)
class Valor(BaseModel):
    id: int
    valor: str
    fecha_hora_lectura: datetime # Pydantic puede manejar datetime al leer
    fecha_dispositivo: datetime
    campo_id: int

    class Config:
        from_attributes = True
# Para actualizar parcialmente un valor
class ValorActualizar(BaseModel):
    campo_id: Optional[int] = None
    valor: Optional[float] = None
    fecha_hora_lectura: Optional[datetime] = None
    magnitud_tipo: Optional[str] = None
# Para respuestas (incluye ID)
class Valor(ValorBase):
    id: int

    class Config:
        orm_mode = True
