from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from matrx_orm import MatrxORM

from app.db.connection import get_db as _get_db
from app.auth.jwt import verify_token

security = HTTPBearer(auto_error=False)


def get_db() -> MatrxORM:
    return _get_db()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    return await verify_token(credentials.credentials)
