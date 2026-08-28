import json
import logging
import time
from datetime import datetime, timezone

from prometheus_client import Counter, Histogram


CHAT_REQUESTS = Counter(
    "chat_requests_total",
    "Total de requests processadas pelo endpoint /chat.",
    ["agent", "status"],
)

CHAT_LATENCY = Histogram(
    "chat_request_duration_seconds",
    "Tempo de processamento do endpoint /chat em segundos.",
    ["agent"],
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", record.getMessage()),
        }

        for field in ("method", "path", "status", "agent", "duration_ms"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


logger = logging.getLogger("getnet.api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def record_chat_request(
    *,
    agent: str,
    status: str,
    method: str,
    path: str,
    started_at: float,
) -> None:
    duration_seconds = time.perf_counter() - started_at
    duration_ms = round(duration_seconds * 1000, 2)

    CHAT_REQUESTS.labels(agent=agent, status=status).inc()
    CHAT_LATENCY.labels(agent=agent).observe(duration_seconds)
    logger.info(
        "chat request completed",
        extra={
            "event": "chat_request_completed",
            "method": method,
            "path": path,
            "status": status,
            "agent": agent,
            "duration_ms": duration_ms,
        },
    )