from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers import auth_controller
from app.database import get_db
from app.deps import get_current_claims
from app.views.auth_views import ClientCredentialsRequest, LoginRequest, RegistroRequest, TokenResponse, UsuarioOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro(payload: RegistroRequest, db: Session = Depends(get_db)):
    return auth_controller.registro(payload, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_controller.login(payload, db)


@router.post("/token", response_model=TokenResponse)
def client_credentials_token(payload: ClientCredentialsRequest):
    return auth_controller.client_credentials_token(payload)


@router.get("/me", response_model=UsuarioOut)
def me(claims: dict = Depends(get_current_claims), db: Session = Depends(get_db)):
    return auth_controller.me(claims, db)
