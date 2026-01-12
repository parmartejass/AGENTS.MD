"""Workflow registry (SSOT): stable IDs -> runner functions."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from myapp.config import JobConfig
from myapp.config_keys import WORKFLOW_KEY_STEPS
from myapp.core.text_transform import ProcessResult, process_text_file


logger = logging.getLogger(__name__)

WORKFLOW_ID_TEXT_TRANSFORM_V1 = "text_transform_v1"


@dataclass(frozen=True)
class Workflow:
    workflow_id: str
    description: str
    run: Callable[[JobConfig, Callable[[], bool]], ProcessResult]


def _run_text_transform_v1(config: JobConfig, is_cancelled: Callable[[], bool]) -> ProcessResult:
    steps = config.workflow.get(WORKFLOW_KEY_STEPS, [])
    return process_text_file(
        input_path=config.input_path,
        output_path=config.output_path,
        steps=steps,
        is_cancelled=is_cancelled,
    )


WORKFLOWS: dict[str, Workflow] = {
    WORKFLOW_ID_TEXT_TRANSFORM_V1: Workflow(
        workflow_id=WORKFLOW_ID_TEXT_TRANSFORM_V1,
        description="Transform a text file line-by-line using JSON-configured steps.",
        run=_run_text_transform_v1,
    ),
}


def get_workflow(workflow_id: str) -> Workflow | None:
    return WORKFLOWS.get(workflow_id)

