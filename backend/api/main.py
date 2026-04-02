from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session

from api.schemas import MapaRequest
from core.cache import CacheClient
from core.config import settings
from core.errors import AppError, app_error_handler, unhandled_error_handler
from core.logging import configure_logging
from core.pipeline import run_pipeline
from db.session import get_cache_client, get_db

# -----------------------------------
# CONFIGURAÇÃO INICIAL
# -----------------------------------

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# -----------------------------------
# HANDLERS DE ERRO
# -----------------------------------

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

# -----------------------------------
# MIDDLEWARE REQUEST ID
# -----------------------------------

@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["x-request-id"] = request_id

    return response


# -----------------------------------
# HEALTH CHECK
# -----------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# -----------------------------------
# ENDPOINT PRINCIPAL
# -----------------------------------

@app.post("/mapa")
def mapa(
    payload: MapaRequest,
    request: Request,
    db: Session = Depends(get_db),
    cache: CacheClient = Depends(get_cache_client),
) -> dict:

    request_id = request.state.request_id

    logger.info(
        "mapa_request_received",
        extra={"request_id": request_id, "input": payload.model_dump()},
    )

    try:
        # 🔥 GARANTIR DETERMINISMO
        reference_date = payload.reference_date or datetime.now(timezone.utc).date()

        result = run_pipeline(
            payload=payload.model_dump(),
            db=db,
            cache=cache,
            request_id=request_id,
            reference_date=reference_date,
        )

    except AppError:
        raise

    except Exception as exc:
        logger.exception(
            "mapa_processing_failed",
            extra={"request_id": request_id},
        )
        raise AppError(
            code="pipeline_error",
            message="Erro ao processar mapa",
            status_code=500,
        ) from exc

    logger.info(
        "mapa_processing_success",
        extra={"request_id": request_id},
    )

    return result