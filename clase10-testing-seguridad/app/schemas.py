from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegistroRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    restaurante: str
    rol: str = "mesero"  # "mesero" | "gerente" — demo only; a real app would not let callers self-assign gerente


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClientCredentialsRequest(BaseModel):
    client_id: str
    client_secret: str


class UsuarioOut(BaseModel):
    id: int
    email: str
    rol: str
    restaurante_id: int


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
    telefono: str  # masked for non-gerente callers — see app/routers/reservas.py
    fecha_hora: datetime
    num_personas: int
    mesa_numero: int
    estado: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumenOut(BaseModel):
    total_reservas: int
    promedio_personas: float
