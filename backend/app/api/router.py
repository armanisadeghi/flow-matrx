from fastapi import APIRouter

from app.api.workflows import router as workflows_router
from app.api.runs import router as runs_router
from app.api.triggers import router as triggers_router
from app.api.ws import router as ws_router

router = APIRouter()
router.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
router.include_router(runs_router, prefix="/runs", tags=["runs"])
router.include_router(triggers_router, prefix="/triggers", tags=["triggers"])
router.include_router(ws_router, tags=["websocket"])
