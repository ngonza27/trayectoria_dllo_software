from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db, set_org_context
from app.security.jwt import InvalidTokenError, decode_and_validate_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        return decode_and_validate_token(credentials.credentials)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}") from exc


def require_role(*allowed_roles: str):
    def dependency(claims: dict = Depends(get_current_claims)) -> dict:
        if claims.get("rol") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return claims

    return dependency


def get_scoped_db(claims: dict = Depends(get_current_claims), db: Session = Depends(get_db)) -> Session:
    set_org_context(db, int(claims["restaurante_id"]))
    return db
