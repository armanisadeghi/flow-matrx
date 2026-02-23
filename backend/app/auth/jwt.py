"""Supabase JWT verification."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status

from app.config import settings


async def verify_token(token: str) -> dict[str, Any]:
    """Verify a Supabase JWT and return the decoded claims."""
    if not settings.supabase_url or not settings.supabase_jwt_secret:
        # Local dev: skip auth
        return {"sub": "dev-user", "role": "authenticated"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return response.json()
