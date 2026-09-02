from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import schemas
from app.analytics import capture
from app.database import get_db
from app.deps import get_current_claims
from app.models import Organizacion, Usuario
from app.security.jwt import create_access_token
from app.security.oauth import InvalidClientError, issue_client_credentials_token
from app.security.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def registro(payload: schemas.RegistroRequest, db: Session = Depends(get_db)):
    """Slide 9 — Authentication starts here: create the identity."""
    if db.query(Usuario).filter(Usuario.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    org = db.query(Organizacion).filter(Organizacion.nombre == payload.organizacion).first()
    if org is None:
        # Found by a load test (slide 27): two requests can both see "no
        # existing org" and both try to INSERT it — this get-or-create is
        # only race-free because we catch the loser's UniqueViolation and
        # fall back to reading the row the winner just created, instead of
        # letting it bubble up as an uncaught 500.
        org = Organizacion(nombre=payload.organizacion)
        db.add(org)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            org = db.query(Organizacion).filter(Organizacion.nombre == payload.organizacion).first()

    usuario = Usuario(
        email=payload.email,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
        organizacion_id=org.id,
    )
    db.add(usuario)
    try:
        db.flush()  # populate usuario.id before commit — see app/database.py on expire_on_commit
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc
    db.commit()

    capture("registro", distinct_id=str(usuario.id), properties={"organizacion": org.nombre})
    return usuario


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Slide 15/18 — the simplified, educational analog of the OAuth 2.0
    Authorization Code flow: a human presents credentials directly to our
    "authorization server" (this endpoint) and receives tokens back. A real
    Authorization Code + PKCE flow adds a redirect and a one-time code
    exchange, which needs a separate hosted login page — see
    docs/security-architecture.md for why that's out of scope for a local demo.
    """
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if usuario is None or not verify_password(payload.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(
        subject=str(usuario.id),
        email=usuario.email,
        rol=usuario.rol,
        organizacion_id=usuario.organizacion_id,
    )
    capture("login", distinct_id=str(usuario.id))
    return schemas.TokenResponse(access_token=token)


@router.post("/token", response_model=schemas.TokenResponse)
def client_credentials_token(payload: schemas.ClientCredentialsRequest):
    """Slide 18 — OAuth 2.0 Client Credentials grant (service-to-service, no human)."""
    try:
        token = issue_client_credentials_token(payload.client_id, payload.client_secret)
    except InvalidClientError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_client") from exc
    return schemas.TokenResponse(access_token=token)


@router.get("/me", response_model=schemas.UsuarioOut)
def me(claims: dict = Depends(get_current_claims), db: Session = Depends(get_db)):
    """Slide 14 — proof the backend validated the JWT before trusting the caller's identity."""
    usuario = db.get(Usuario, int(claims["sub"])) if claims.get("sub") else None
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return usuario
