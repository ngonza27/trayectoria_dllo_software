from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dal import restaurante_dal, usuario_dal
from app.dal.models import Usuario
from app.security.jwt import create_access_token
from app.security.oauth import issue_client_credentials_token
from app.security.passwords import hash_password, verify_password
from app.services.analytics_service import capture
from app.views.auth_views import LoginRequest, RegistroRequest


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def registrar(db: Session, payload: RegistroRequest) -> Usuario:
    if usuario_dal.get_by_email(db, payload.email):
        raise EmailAlreadyRegisteredError()

    restaurante = restaurante_dal.get_by_nombre(db, payload.restaurante)
    if restaurante is None:
        restaurante = restaurante_dal.create(db, payload.restaurante)

    usuario = Usuario(
        email=payload.email,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
        restaurante_id=restaurante.id,
    )
    usuario_dal.create(db, usuario)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyRegisteredError() from exc
    db.commit()

    capture("registro", distinct_id=str(usuario.id), properties={"restaurante": restaurante.nombre})
    return usuario


def login(db: Session, payload: LoginRequest) -> str:
    usuario = usuario_dal.get_by_email(db, payload.email)
    if usuario is None or not verify_password(payload.password, usuario.password_hash):
        raise InvalidCredentialsError()

    token = create_access_token(
        subject=str(usuario.id),
        email=usuario.email,
        rol=usuario.rol,
        restaurante_id=usuario.restaurante_id,
    )
    capture("login", distinct_id=str(usuario.id))
    return token


def issue_service_token(client_id: str, client_secret: str) -> str:
    return issue_client_credentials_token(client_id, client_secret)


def get_usuario_by_id(db: Session, usuario_id: int) -> Usuario | None:
    return usuario_dal.get_by_id(db, usuario_id)
