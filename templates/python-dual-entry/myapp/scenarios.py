"""Scenario loader (SSOT) for config-driven tests and CLI verification."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myapp.config import JobConfig
from myapp.config_keys import (
    EXPECTED_KEY_OUTPUT_PATH,
    EXPECTED_KEY_SUCCESS,
    JOB_KEY_INPUT_PATH,
    JOB_KEY_OUTPUT_PATH,
    JOB_KEY_WORKFLOW,
    JOB_KEY_WORKFLOW_ID,
    SCENARIO_KEY_DESCRIPTION,
    SCENARIO_KEY_EXPECTED,
    SCENARIO_KEY_ID,
    SCENARIO_KEY_JOB,
)
from myapp.errors import ConfigError


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ScenarioExpected:
    success: bool = True
    output_path: Path | None = None


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    description: str
    job: JobConfig
    expected: ScenarioExpected
    source_path: Path


def list_scenario_files(scenarios_dir: Path) -> list[Path]:
    if not scenarios_dir.exists():
        return []
    return sorted(p for p in scenarios_dir.glob("*.json") if p.is_file())


def load_scenario(scenario_path: Path) -> ScenarioSpec:
    scenario_path = Path(scenario_path)
    base_dir = scenario_path.parent

    try:
        raw = json.loads(scenario_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Scenario file not found: {scenario_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in scenario file: {scenario_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(f"Scenario root must be an object: {scenario_path}")

    scenario_id = raw.get(SCENARIO_KEY_ID)
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        raise ConfigError(f"Missing/invalid '{SCENARIO_KEY_ID}' in: {scenario_path}")

    description = raw.get(SCENARIO_KEY_DESCRIPTION) or ""
    if not isinstance(description, str):
        raise ConfigError(f"Invalid '{SCENARIO_KEY_DESCRIPTION}' in: {scenario_path}")

    job_raw = raw.get(SCENARIO_KEY_JOB)
    if not isinstance(job_raw, dict):
        raise ConfigError(f"Missing/invalid '{SCENARIO_KEY_JOB}' in: {scenario_path}")

    workflow_id = job_raw.get(JOB_KEY_WORKFLOW_ID)
    if not isinstance(workflow_id, str) or not workflow_id.strip():
        raise ConfigError(f"Missing/invalid '{JOB_KEY_WORKFLOW_ID}' in: {scenario_path}")

    input_path = _resolve_path(job_raw.get(JOB_KEY_INPUT_PATH), base_dir, JOB_KEY_INPUT_PATH, scenario_path)
    output_path = _resolve_path(job_raw.get(JOB_KEY_OUTPUT_PATH), base_dir, JOB_KEY_OUTPUT_PATH, scenario_path)

    workflow: Any = job_raw.get(JOB_KEY_WORKFLOW, {})
    if workflow is None:
        workflow = {}
    if not isinstance(workflow, dict):
        raise ConfigError(f"Invalid '{JOB_KEY_WORKFLOW}' in: {scenario_path}")

    job = JobConfig(workflow_id=workflow_id, input_path=input_path, output_path=output_path, workflow=workflow)

    expected_raw = raw.get(SCENARIO_KEY_EXPECTED, {})
    if expected_raw is None:
        expected_raw = {}
    if not isinstance(expected_raw, dict):
        raise ConfigError(f"Invalid '{SCENARIO_KEY_EXPECTED}' in: {scenario_path}")

    expected_success = expected_raw.get(EXPECTED_KEY_SUCCESS, True)
    if not isinstance(expected_success, bool):
        raise ConfigError(f"Invalid '{EXPECTED_KEY_SUCCESS}' in: {scenario_path}")

    expected_output_path: Path | None = None
    if EXPECTED_KEY_OUTPUT_PATH in expected_raw:
        expected_output_path = _resolve_path(
            expected_raw.get(EXPECTED_KEY_OUTPUT_PATH),
            base_dir,
            EXPECTED_KEY_OUTPUT_PATH,
            scenario_path,
            allow_none=True,
        )

    expected = ScenarioExpected(success=expected_success, output_path=expected_output_path)

    logger.debug("Loaded scenario %s from %s", scenario_id, scenario_path)
    return ScenarioSpec(
        scenario_id=scenario_id,
        description=description,
        job=job,
        expected=expected,
        source_path=scenario_path,
    )


def _resolve_path(
    value: Any,
    base_dir: Path,
    key: str,
    scenario_path: Path,
    *,
    allow_none: bool = False,
) -> Path | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Missing/invalid '{key}' in: {scenario_path}")

    path = Path(value)
    if path.is_absolute():
        return path
    return base_dir / path

