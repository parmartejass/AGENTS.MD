"""Governance-core package: the stable public API for governance validation.

Public members are listed in ``__all__``:

    run_checks(request) -> plain dictionary
    resolve_documents(request) -> plain dictionary
    main(argv) -> process exit code

The request accepts ``repo_root``, ``governance_root``, ``mode`` (``full``,
``docs``, or ``project_docs``), and ``fail_on_safety_warnings``. Validation is
read-only; strict mode promotes Python-safety warnings to failures. Invalid
requests and unexpected failures are returned as explicit
FAILED_VALIDATION/FAILED results. ``__main__.py`` launches ``main`` when the
package runs as ``python -m scripts.check_governance_core`` from the governance
root; callers use only these public members, never private modules.
"""

from scripts.check_governance_core._api import resolve_documents, run_checks
from scripts.check_governance_core._cli import main


__all__ = ["main", "resolve_documents", "run_checks"]
