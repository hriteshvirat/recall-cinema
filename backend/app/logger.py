import json
import logging
import time
import uuid
from typing import Any, Dict, Optional
from contextlib import contextmanager

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("recall")

def sanitize_data(data: Any) -> Any:
    """Recursively strip sensitive keys like api_key, password, token."""
    if isinstance(data, dict):
        clean = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(secret in k_lower for secret in ["password", "key", "token", "secret", "auth"]):
                clean[k] = "[REDACTED]"
            else:
                clean[k] = sanitize_data(v)
        return clean
    elif isinstance(data, list):
        return [sanitize_data(i) for i in data]
    return data

def log_operation(
    operation: str,
    movie_id: Optional[str] = None,
    request_id: Optional[str] = None,
    duration_ms: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None
):
    """Structured JSON log for RECALL operations."""
    req_id = request_id or str(uuid.uuid4())[:8]
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "request_id": req_id,
        "operation": operation,
        "movie_id": movie_id or "N/A",
        "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
        "success": success,
        "error": error
    }
    if extra:
        payload["extra"] = sanitize_data(extra)
    
    msg = json.dumps(payload)
    if success:
        logger.info(msg)
    else:
        logger.error(msg)

@contextmanager
def log_block(operation: str, movie_id: Optional[str] = None, request_id: Optional[str] = None):
    """Context manager timing an operation and logging result."""
    start_time = time.time()
    req_id = request_id or str(uuid.uuid4())[:8]
    try:
        yield req_id
        elapsed = (time.time() - start_time) * 1000
        log_operation(operation, movie_id=movie_id, request_id=req_id, duration_ms=elapsed, success=True)
    except Exception as exc:
        elapsed = (time.time() - start_time) * 1000
        log_operation(operation, movie_id=movie_id, request_id=req_id, duration_ms=elapsed, success=False, error=str(exc))
        raise
