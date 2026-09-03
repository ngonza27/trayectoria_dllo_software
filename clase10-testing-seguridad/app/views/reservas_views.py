from datetime import datetime

from pydantic import BaseModel, Field


class ReservaCreate(BaseModel):
    cliente_nombre: str
    telefono: str = Field(min_length=7, max_length=20)
    fecha_hora: datetime
    num_personas: int = Field(gt=0)
    mesa_numero: int = Field(gt=0)


class ReservaUpdate(BaseModel):
    estado: str | None = None
    mesa_numero: int | None = None
    num_personas: int | None = None


class ReservaOut(BaseModel):
    id: int
    restaurante_id: int
    cliente_nombre: str
    telefono: str
    fecha_hora: datetime
    num_personas: int
    mesa_numero: int
    estado: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumenOut(BaseModel):
    total_reservas: int
    promedio_personas: float
