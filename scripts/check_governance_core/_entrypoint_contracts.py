from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple


ENTRYPOINT_CONTRACTS_REL = "scripts/entrypoint_contracts.json"


@dataclass(frozen=True)
class RuntimeContract:
    entrypoint_token: str
    extension: str


@dataclass(frozen=True)
class DocsContract:
    router_pattern: str
    numbered_governance_folder_regex: str
    dated_evidence_folder_regex: str
    dated_evidence_authority: str
    minimum_public_leaf_count: int
    plain_folder_default: str
    numbered_governance_folder: str
    dated_evidence_folder: str
    identity_files: tuple[str, ...]


def _clean_relative_path(value: str, *, label: str) -> Tuple[str | None, List[str]]:
    errors: List[str] = []
    cleaned = value.strip().replace("\\", "/").strip("/")
    if not cleaned:
        return None, [f"Invalid empty {label} path."]
    if re.match(r"^[A-Za-z]:", cleaned):
        return None, [f"Invalid {label} path '{value}'; absolute drive-qualified paths are forbidden."]

    parts = cleaned.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        errors.append(f"Invalid {label} path '{value}'; path segments must stay within repo boundaries.")
        return None, errors
    return cleaned, errors


def _require_dict(container: Dict[str, Any], key: str, *, label: str, errors: List[str]) -> Dict[str, Any] | None:
    value = container.get(key)
    if not isinstance(value, dict):
        errors.append(f"Missing object key '{label}' in {ENTRYPOINT_CONTRACTS_REL}.")
        return None
    return value


def _require_str(container: Dict[str, Any], key: str, *, label: str, errors: List[str]) -> str | None:
    value = container.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"Missing string key '{label}' in {ENTRYPOINT_CONTRACTS_REL}.")
        return None
    return value


def _validate_runtime_language_contracts(
    languages: Dict[str, Any],
    *,
    errors: List[str],
) -> None:
    if not languages:
        errors.append(f"Missing object key 'runtime_code.languages' in {ENTRYPOINT_CONTRACTS_REL}.")
        return

    for language_name, language_payload in languages.items():
        if not isinstance(language_payload, dict):
            errors.append(
                f"Invalid object key 'runtime_code.languages.{language_name}' in {ENTRYPOINT_CONTRACTS_REL}."
            )
            continue
        artifact_kinds = language_payload.get("artifact_kinds")
        if not isinstance(artifact_kinds, dict) or not artifact_kinds:
            errors.append(
                f"Missing object key 'runtime_code.languages.{language_name}.artifact_kinds' "
                f"in {ENTRYPOINT_CONTRACTS_REL}."
            )
            continue
        for artifact_kind, artifact_payload in artifact_kinds.items():
            if not isinstance(artifact_payload, dict):
                errors.append(
                    f"Invalid object key 'runtime_code.languages.{language_name}.artifact_kinds.{artifact_kind}' "
                    f"in {ENTRYPOINT_CONTRACTS_REL}."
                )
                continue
            for field_name in ("entrypoint_token", "extension"):
                _require_str(
                    artifact_payload,
                    field_name,
                    label=f"runtime_code.languages.{language_name}.artifact_kinds.{artifact_kind}.{field_name}",
                    errors=errors,
                )


def validate_contract_schema(payload: dict[str, Any]) -> List[str]:
    errors: List[str] = []

    runtime = _require_dict(payload, "runtime_code", label="runtime_code", errors=errors)
    docs = _require_dict(payload, "docs", label="docs", errors=errors)
    if runtime is None or docs is None:
        return errors

    _require_str(runtime, "filename_pattern", label="runtime_code.filename_pattern", errors=errors)
    languages = runtime.get("languages")
    if not isinstance(languages, dict):
        errors.append(f"Missing object key 'runtime_code.languages' in {ENTRYPOINT_CONTRACTS_REL}.")
    else:
        _validate_runtime_language_contracts(languages, errors=errors)

    _require_str(docs, "router_pattern", label="docs.router_pattern", errors=errors)
    authority_resolution = _require_dict(
        docs, "authority_resolution", label="docs.authority_resolution", errors=errors
    )
    if authority_resolution is not None:
        for field_name in (
            "numbered_governance_folder_regex",
            "dated_evidence_folder_regex",
            "dated_evidence_authority",
        ):
            _require_str(
                authority_resolution,
                field_name,
                label=f"docs.authority_resolution.{field_name}",
                errors=errors,
            )

    public_leaf_model = _require_dict(
        docs, "public_leaf_model", label="docs.public_leaf_model", errors=errors
    )
    if public_leaf_model is not None:
        minimum_public_leaf_count = public_leaf_model.get("minimum_public_leaf_count")
        if not isinstance(minimum_public_leaf_count, int) or minimum_public_leaf_count < 0:
            errors.append(
                "Missing integer key 'docs.public_leaf_model.minimum_public_leaf_count' "
                f"in {ENTRYPOINT_CONTRACTS_REL}."
            )

    public_leaf_patterns = _require_dict(
        docs, "public_leaf_patterns", label="docs.public_leaf_patterns", errors=errors
    )
    if public_leaf_patterns is not None:
        for field_name in (
            "plain_folder_default",
            "numbered_governance_folder",
            "dated_evidence_folder",
        ):
            _require_str(
                public_leaf_patterns,
                field_name,
                label=f"docs.public_leaf_patterns.{field_name}",
                errors=errors,
            )

    exceptions = _require_dict(
        docs, "explicit_family_exceptions", label="docs.explicit_family_exceptions", errors=errors
    )
    if exceptions is not None:
        identity_files = exceptions.get("identity_files")
        if not isinstance(identity_files, list) or not all(
            isinstance(item, str) and item.strip() for item in identity_files
        ):
            errors.append(
                "Missing string-list key 'docs.explicit_family_exceptions.identity_files' "
                f"in {ENTRYPOINT_CONTRACTS_REL}."
            )

    return errors


def load_entrypoint_contracts(governance_root: Path) -> Tuple[dict[str, Any], List[str]]:
    path = governance_root / ENTRYPOINT_CONTRACTS_REL
    if not path.is_file():
        return {}, [f"Missing entrypoint-contract registry: {path}"]

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"Invalid JSON in {path}: {exc}"]

    errors: List[str] = []
    if payload.get("version") != 1:
        errors.append(f"Unsupported entrypoint-contract registry version in {path}.")

    runtime = payload.get("runtime_code")
    docs = payload.get("docs")
    if not isinstance(runtime, dict):
        errors.append(f"Missing object key 'runtime_code' in {path}.")
    if not isinstance(docs, dict):
        errors.append(f"Missing object key 'docs' in {path}.")
    if not errors:
        errors.extend(validate_contract_schema(payload))

    return payload, errors


def docs_contract_from_payload(payload: dict[str, Any]) -> DocsContract:
    docs = payload["docs"]
    authority_resolution = docs["authority_resolution"]
    public_leaf_model = docs["public_leaf_model"]
    public_leaf_patterns = docs["public_leaf_patterns"]
    exceptions = docs["explicit_family_exceptions"]
    return DocsContract(
        router_pattern=str(docs["router_pattern"]),
        numbered_governance_folder_regex=str(authority_resolution["numbered_governance_folder_regex"]),
        dated_evidence_folder_regex=str(authority_resolution["dated_evidence_folder_regex"]),
        dated_evidence_authority=str(authority_resolution["dated_evidence_authority"]),
        minimum_public_leaf_count=int(public_leaf_model["minimum_public_leaf_count"]),
        plain_folder_default=str(public_leaf_patterns["plain_folder_default"]),
        numbered_governance_folder=str(public_leaf_patterns["numbered_governance_folder"]),
        dated_evidence_folder=str(public_leaf_patterns["dated_evidence_folder"]),
        identity_files=tuple(str(item) for item in exceptions["identity_files"]),
    )


def runtime_contract_from_payload(
    payload: dict[str, Any], *, language: str, artifact_kind: str = "executable"
) -> RuntimeContract:
    languages = payload["runtime_code"]["languages"]
    contract = languages[language]["artifact_kinds"][artifact_kind]
    return RuntimeContract(
        entrypoint_token=str(contract["entrypoint_token"]),
        extension=str(contract["extension"]),
    )


def resolve_docs_authority(folder_name: str, docs_contract: DocsContract) -> str:
    numbered = re.match(docs_contract.numbered_governance_folder_regex, folder_name)
    if numbered:
        return str(numbered.group("authority"))
    if re.match(docs_contract.dated_evidence_folder_regex, folder_name):
        return docs_contract.dated_evidence_authority
    return folder_name


def resolve_docs_router_filename(folder_name: str, docs_contract: DocsContract) -> str:
    authority = resolve_docs_authority(folder_name, docs_contract)
    return docs_contract.router_pattern.replace("<authority>", authority)


def resolve_primary_leaf_filename(folder_name: str, docs_contract: DocsContract) -> str:
    authority = resolve_docs_authority(folder_name, docs_contract)
    if re.match(docs_contract.dated_evidence_folder_regex, folder_name):
        pattern = docs_contract.dated_evidence_folder
    elif re.match(docs_contract.numbered_governance_folder_regex, folder_name):
        pattern = docs_contract.numbered_governance_folder
    else:
        pattern = docs_contract.plain_folder_default
    return pattern.replace("<authority>", authority)


def resolve_runtime_entrypoint_filename(
    folder_name: str,
    payload: dict[str, Any],
    *,
    language: str = "python",
    artifact_kind: str = "executable",
) -> str:
    runtime_contract = runtime_contract_from_payload(payload, language=language, artifact_kind=artifact_kind)
    pattern = str(payload["runtime_code"]["filename_pattern"])
    return (
        pattern.replace("<authority>", folder_name)
        .replace("<entrypoint_token>", runtime_contract.entrypoint_token)
        .replace("<extension>", runtime_contract.extension)
    )


def validate_registry_paths(payload: dict[str, Any]) -> List[str]:
    errors: List[str] = []
    ssot_owner = payload.get("ssot_owner", {})
    if isinstance(ssot_owner, dict):
        for family, owner in ssot_owner.items():
            if not isinstance(owner, str):
                errors.append(f"Invalid ssot_owner.{family}; expected string path.")
                continue
            _path, path_errors = _clean_relative_path(owner, label=f"ssot_owner.{family}")
            errors.extend(path_errors)
    elif isinstance(ssot_owner, str):
        _path, path_errors = _clean_relative_path(ssot_owner, label="ssot_owner")
        errors.extend(path_errors)
    else:
        errors.append("entrypoint-contract registry must define ssot_owner.")
    return errors


def ssot_owner_path_from_payload(payload: dict[str, Any], family: str) -> str | None:
    ssot_owner = payload.get("ssot_owner")
    if not isinstance(ssot_owner, dict):
        return None
    owner = ssot_owner.get(family)
    if not isinstance(owner, str) or not owner.strip():
        return None
    return owner
