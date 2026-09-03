from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.security.oauth import InvalidClientError
from app.services import auth_service
from app.services.auth_service import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.views.auth_views import ClientCredentialsRequest, LoginRequest, RegistroRequest, TokenResponse, UsuarioOut


def registro(payload: RegistroRequest, db: Session) -> UsuarioOut:
    try:
        return auth_service.registrar(db, payload)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc


def login(payload: LoginRequest, db: Session) -> TokenResponse:
    try:
        token = auth_service.login(db, payload)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
    return TokenResponse(access_token=token)


def client_credentials_token(payload: ClientCredentialsRequest) -> TokenResponse:
    try:
        token = auth_service.issue_service_token(payload.client_id, payload.client_secret)
    except InvalidClientError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_client") from exc
    return TokenResponse(access_token=token)


def me(claims: dict, db: Session) -> UsuarioOut:
    usuario = auth_service.get_usuario_by_id(db, int(claims["sub"])) if claims.get("sub") else None
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return usuario
