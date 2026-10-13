import logging
from functools import lru_cache

from fastapi import HTTPException

from app.config import settings
from app.repositories.json_store import JsonStore, StoreError

logger = logging.getLogger(__name__)


@lru_cache
def get_store() -> JsonStore:
    return JsonStore(settings.store_dir, settings.seed_file)


def report_store_error(error: StoreError) -> None:
    logger.exception("No se pudo acceder al almacén de datos.", exc_info=error)
    raise HTTPException(
        status_code=503,
        detail="El almacén de datos no está disponible o requiere revisión.",
    ) from error
