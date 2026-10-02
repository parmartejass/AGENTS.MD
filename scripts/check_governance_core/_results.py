from __future__ import annotations


API_VERSION = 1


def _check_failure(status: str, errors: list[str]) -> dict[str, object]:
    return {
        "api_version": API_VERSION,
        "status": status,
        "checks": [],
        "planned": [],
        "eligible": [],
        "executed": [],
        "skipped": [],
        "failed": [],
        "errors": errors,
        "warnings": [],
    }


def _document_result(
    status: str, documents: list[str], errors: list[str]
) -> dict[str, object]:
    return {
        "api_version": API_VERSION,
        "status": status,
        "documents": documents,
        "errors": errors,
    }
