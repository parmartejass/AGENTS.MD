from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from scripts.check_governance_core._engine import execute, resolve_documents_request
from scripts.check_governance_core._results import _check_failure, _document_result


_CHECK_REQUEST_KEYS = frozenset({"repo_root", "governance_root", "mode", "fail_on_safety_warnings"})
_DOCUMENT_REQUEST_KEYS = frozenset({"repo_root", "governance_root"})


def _unknown_keys(request: Mapping[str, object], allowed: frozenset[str]) -> str | None:
    unknown = sorted(str(key) for key in request if key not in allowed)
    return f"unsupported request key(s): {', '.join(unknown)}" if unknown else None


def _validate_root_fields(request: Mapping[str, object]) -> str | None:
    for field in ("repo_root", "governance_root"):
        value = request.get(field)
        if value is not None and not isinstance(value, (str, Path)):
            return f"{field} must be a path string, Path, or null"
        if field in request and isinstance(value, (str, Path)) and not str(value).strip():
            return f"{field} must not be empty when provided"
    return None


def _validate_check_request(request: Mapping[str, object]) -> str | None:
    error = _unknown_keys(request, _CHECK_REQUEST_KEYS) or _validate_root_fields(request)
    if error:
        return error
    if not isinstance(request.get("mode", "full"), str):
        return "mode must be a string"
    if not isinstance(request.get("fail_on_safety_warnings", False), bool):
        return "fail_on_safety_warnings must be a boolean"
    return None


def run_checks(request: Mapping[str, object]) -> dict[str, object]:
    """Run deterministic checks through the only supported programmatic boundary.

    Inputs and outputs contain plain data only. The function does not mutate the
    caller's mapping. Unsupported keys are rejected so extension remains an
    explicit public-contract change.
    """

    if not isinstance(request, Mapping):
        return _check_failure("FAILED_VALIDATION", ["request must be a mapping"])
    validation_error = _validate_check_request(request)
    if validation_error:
        return _check_failure("FAILED_VALIDATION", [validation_error])
    try:
        return execute(dict(request))
    except ValueError as exc:
        return _check_failure("FAILED_VALIDATION", [str(exc)])
    except Exception as exc:  # public boundary converts crashes into explicit failure
        return _check_failure("FAILED", [f"internal governance-check failure: {type(exc).__name__}: {exc}"])


def resolve_documents(request: Mapping[str, object]) -> dict[str, object]:
    """Return the canonical router-owned governance research corpus.

    Accepted inputs are ``repo_root`` and ``governance_root``. The read-only
    result contains ``api_version``, terminal ``status``, ``AGENTS.md`` and
    ``Orchestration.md`` followed by ordered terminal Markdown leaves reachable from
    ``docs/agents/agents_index.md``, and ``errors``. Routing-manifest membership
    does not define this corpus. Invalid, aliased, escaped, missing, cyclic, or
    duplicate topology returns an empty document list and explicit failure.
    """

    if not isinstance(request, Mapping):
        return _document_result("FAILED_VALIDATION", [], ["request must be a mapping"])
    validation_error = _unknown_keys(request, _DOCUMENT_REQUEST_KEYS) or _validate_root_fields(request)
    if validation_error:
        return _document_result("FAILED_VALIDATION", [], [validation_error])
    try:
        return resolve_documents_request(dict(request))
    except ValueError as exc:
        return _document_result("FAILED_VALIDATION", [], [str(exc)])
    except Exception as exc:
        return _document_result("FAILED", [], [f"internal governance-document resolution failure: {type(exc).__name__}: {exc}"])
