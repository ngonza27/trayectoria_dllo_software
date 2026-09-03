from pydantic import BaseModel, EmailStr, Field


class RegistroRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    restaurante: str
    rol: str = "mesero"


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
