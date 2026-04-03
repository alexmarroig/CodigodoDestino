from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api.schemas import FeedbackEventRequest, HoraryRequest, LifeEventRequest, MapaRequest
from core.cache import CacheClient
from core.config import settings
from core.errors import AppError, app_error_handler, unhandled_error_handler
from core.feedback_events import save_feedback_event
from core.life_events import save_life_event
from core.logging import configure_logging
from core.pipeline import run_pipeline
from db.session import get_cache_client, get_db, initialize_database
from engine.horary import analyze_horary

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id
    started_at = perf_counter()

    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    response.headers["x-process-time-ms"] = str(round((perf_counter() - started_at) * 1000, 2))
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/mapa")
def mapa(
    payload: MapaRequest,
    request: Request,
    db: Session = Depends(get_db),
    cache: CacheClient = Depends(get_cache_client),
) -> dict:
    request_id = request.state.request_id
    payload_data = payload.model_dump(mode="json", exclude_none=True)
    reference_date = payload.reference_date or datetime.now(timezone.utc).date()

    logger.info(
        "mapa_request_received",
        extra={"request_id": request_id},
    )

    try:
        result = run_pipeline(
            payload=payload_data,
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
            message="Unexpected error while processing /mapa.",
            status_code=500,
        ) from exc

    logger.info(
        "mapa_processing_success",
        extra={"request_id": request_id},
    )
    return result


@app.post("/horaria")
def horaria(
    payload: HoraryRequest,
    request: Request,
) -> dict:
    request_id = request.state.request_id
    payload_data = payload.model_dump(mode="json", exclude_none=True)

    logger.info(
        "horaria_request_received",
        extra={"request_id": request_id},
    )

    try:
        result = analyze_horary(payload_data)
    except Exception as exc:
        logger.exception(
            "horaria_processing_failed",
            extra={"request_id": request_id},
        )
        raise AppError(
            code="horary_error",
            message="Unexpected error while processing /horaria.",
            status_code=500,
        ) from exc

    result["request_id"] = request_id
    logger.info(
        "horaria_processing_success",
        extra={"request_id": request_id},
    )
    return result


@app.post("/life-event")
def life_event(
    payload: LifeEventRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    request_id = request.state.request_id
    payload_data = payload.model_dump(mode="json", exclude_none=True)

    logger.info(
        "life_event_received",
        extra={"request_id": request_id},
    )

    try:
        result = save_life_event(payload_data, db)
    except AppError:
        raise
    except Exception as exc:
        logger.exception(
            "life_event_failed",
            extra={"request_id": request_id},
        )
        raise AppError(
            code="life_event_error",
            message="Unexpected error while processing /life-event.",
            status_code=500,
        ) from exc

    result["request_id"] = request_id
    logger.info(
        "life_event_success",
        extra={"request_id": request_id},
    )
    return result


@app.post("/feedback-event")
def feedback_event(
    payload: FeedbackEventRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    request_id = request.state.request_id
    payload_data = payload.model_dump(mode="json", exclude_none=True)

    logger.info(
        "feedback_event_received",
        extra={"request_id": request_id},
    )

    try:
        result = save_feedback_event(payload_data, db)
    except AppError:
        raise
    except Exception as exc:
        logger.exception(
            "feedback_event_failed",
            extra={"request_id": request_id},
        )
        raise AppError(
            code="feedback_event_error",
            message="Unexpected error while processing /feedback-event.",
            status_code=500,
        ) from exc

    result["request_id"] = request_id
    logger.info(
        "feedback_event_success",
        extra={"request_id": request_id},
    )
    return result
