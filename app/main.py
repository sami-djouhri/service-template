from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Response

from app import health
from app.auth import Principal, current_user
from app.config import settings
from app.logging_config import configure_logging, get_logger
from app.mqtt import publisher

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("service.startup", service=settings.service_name, version=settings.service_version)
    try:
        publisher.connect()
    except Exception as exc:
        log.warning("mqtt.connect_failed", error=str(exc))
    yield
    publisher.disconnect()
    log.info("service.shutdown")


app = FastAPI(
    title=settings.service_name,
    version=settings.service_version,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url=None,
    lifespan=lifespan,
)


# Readiness-Check aus der env verdrahten: HEALTH_DB_PATH gesetzt -> DB-Probe.
# Neue Dienste erben so eine echte Readiness ohne Code; wer eigene Checks braucht,
# ruft health.register_check(...) beim Startup auf.
if settings.health_db_path:
    health.register_check("db", health.sqlite_check(settings.health_db_path))


@app.get("/health")
async def health_endpoint(response: Response) -> dict:
    healthy, checks = await health.run_checks(timeout=settings.health_check_timeout)
    body = {
        "status": "ok" if healthy else "degraded",
        "service": settings.service_name,
        "version": settings.service_version,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    if checks:
        body["checks"] = checks
    if not healthy:
        response.status_code = 503
    return body


@app.get("/api/me")
async def me(principal: Principal = Depends(current_user)) -> dict:
    return principal.model_dump()
