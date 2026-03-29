from __future__ import annotations

import json
import logging
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)

DEFAULT_HTTP_TIMEOUT = 30
MAX_RETRY_DELAY_SECONDS = 300
SENSITIVE_KEYS = {
    "access_token",
    "authorization",
    "client_secret",
    "refresh_token",
    "token",
}


@dataclass(frozen=True)
class JsonResponse:
    status: int
    data: Any
    headers: dict[str, str]


class RuntimeRequestError(RuntimeError):
    """Raised when a runtime HTTP request returns invalid JSON."""


class UsageError(ValueError):
    """Raised for controlled CLI usage failures."""


def configure_logging(*, level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stderr)


def load_env(start_dir: Path, *, max_levels: int = 8) -> Path | None:
    current = start_dir.resolve()
    for _ in range(max_levels):
        env_path = current / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip("'\""))
            return env_path
        if current.parent == current:
            break
        current = current.parent
    return None


def request_json(
    method: str,
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, str] | None = None,
    form_data: Mapping[str, str] | None = None,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
    context: str,
) -> JsonResponse:
    full_url = url + ("?" + urlencode(params) if params else "")
    request_headers = dict(headers or {})
    request_body = None
    if form_data is not None:
        request_body = urlencode(form_data).encode()
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

    request = Request(full_url, data=request_body, headers=request_headers, method=method.upper())
    try:
        with urlopen(request, timeout=timeout) as response:
            raw_body = response.read()
            data = _decode_json_payload(raw_body, context=f"{context} response")
            return JsonResponse(
                status=int(response.status),
                data=data,
                headers=dict(response.headers.items()),
            )
    except HTTPError as exc:
        raw_body = exc.read() if exc.fp else str(exc).encode()
        data = _decode_error_payload(raw_body, context=f"{context} error response")
        return JsonResponse(
            status=int(exc.code),
            data=data,
            headers=dict(exc.headers.items()) if exc.headers is not None else {},
        )
    except URLError as exc:
        raise RuntimeRequestError(f"{context} request failed: {exc.reason}") from exc


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                sanitized[key] = "<redacted>"
            else:
                sanitized[key] = sanitize_payload(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    return value


def summarize_payload(value: Any, *, max_length: int = 300) -> str:
    sanitized = sanitize_payload(value)
    if isinstance(sanitized, (dict, list)):
        rendered = json.dumps(sanitized, ensure_ascii=False, sort_keys=True, default=str)
    else:
        rendered = str(sanitized)
    if len(rendered) <= max_length:
        return rendered
    return rendered[: max_length - 3] + "..."


def atomic_write_text(target: Path, content: str, *, encoding: str = "utf-8", mode: int = 0o600) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            dir=str(target.parent),
            delete=False,
            prefix=f".{target.name}.",
            suffix=".tmp",
        ) as handle:
            temp_path = Path(handle.name)
            try:
                os.chmod(temp_path, mode)
            except OSError:
                logger.debug("Could not set temporary file mode for %s", temp_path, exc_info=True)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temp_path.replace(target)
        try:
            os.chmod(target, mode)
        except OSError:
            logger.debug("Could not set file mode for %s", target, exc_info=True)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink(missing_ok=True)


def write_stdout_line(text: str = "") -> None:
    sys.stdout.write(f"{text}\n")


def write_json_stdout(payload: Any) -> None:
    sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    sys.stdout.write("\n")


def parse_retry_delay_seconds(
    headers: Mapping[str, str] | None,
    *,
    default_seconds: int = 60,
    max_seconds: int = MAX_RETRY_DELAY_SECONDS,
) -> int:
    normalized = {str(key).lower(): str(value) for key, value in (headers or {}).items()}
    retry_after = normalized.get("retry-after")
    if retry_after:
        try:
            return max(1, min(int(float(retry_after)), max_seconds))
        except ValueError:
            logger.debug("Ignoring non-numeric Retry-After header: %s", retry_after)

    reset_at = normalized.get("x-rate-limit-reset")
    if reset_at:
        try:
            delay = int(float(reset_at)) - int(time.time())
            return max(1, min(delay, max_seconds))
        except ValueError:
            logger.debug("Ignoring non-numeric X-Rate-Limit-Reset header: %s", reset_at)

    return max(1, min(default_seconds, max_seconds))


def parse_int_arg(
    raw_value: str,
    *,
    flag_name: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise UsageError(f"{flag_name} must be an integer.") from exc

    if minimum is not None and value < minimum:
        raise UsageError(f"{flag_name} must be >= {minimum}.")
    if maximum is not None and value > maximum:
        raise UsageError(f"{flag_name} must be <= {maximum}.")
    return value


def _decode_json_payload(raw_body: bytes, *, context: str) -> Any:
    try:
        return json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeRequestError(f"{context} was not valid JSON.") from exc


def _decode_error_payload(raw_body: bytes, *, context: str) -> Any:
    text = raw_body.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("%s was not valid JSON; using text payload.", context)
        return text
