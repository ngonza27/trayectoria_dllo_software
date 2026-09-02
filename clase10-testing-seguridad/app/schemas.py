from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegistroRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    organizacion: str
    rol: str = "usuario"  # "usuario" | "admin" — demo only; a real app would not let callers self-assign admin


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
    organizacion_id: int


class CuentaCreate(BaseModel):
    titular: str
    numero_cuenta: str = Field(min_length=8, max_length=20)
    saldo: float = 0


class CuentaUpdate(BaseModel):
    titular: str | None = None
    saldo: float | None = None


class CuentaOut(BaseModel):
    id: int
    organizacion_id: int
    titular: str
    numero_cuenta: str  # masked for non-admin callers — see app/routers/accounts.py
    saldo: float
    created_at: datetime

    model_config = {"from_attributes": True}
