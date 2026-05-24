from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    path: str
    message: str


@dataclass(frozen=True)
class PythonRoot:
    path: str
    enforcement_mode: str
    owner: str
