---
doc_type: policy
ssot_owner: docs/agents/governance/coding/coding.md
update_trigger: native package mechanics, the code-size review value, or the runtime-path rule change
---

# Coding

Jurisdiction: packaged-folder code mechanics, the code-size review value, and the single runtime path.

## Packaged-folder code mechanics

- Config payloads, fixtures, schemas, and generated artifacts are not separate packaged folders unless they own runtime behavior.
- Code private internals MUST follow the private-name convention in the table below.

```yaml
baseline:
  interface: the language's native package and module system
  pattern: "per language, one row of the table below: the native package mechanism, its public-entry file and member declaration, its private-name convention, its launcher form, and the deterministic witness that enforces them"
  reason: "interpreters, import systems, packaging tools, and test runners resolve the native mechanism directly; a custom entry-file convention is a wrapper that needs import-path manipulation and a private checker rule to hold"
  exception: none
```

| Language | Packaged folder | Public entrypoint and members | Private internals | Launcher | Source | Witness |
| --- | --- | --- | --- | --- | --- | --- |
| Python | regular package: a directory with `__init__.py` | `__init__.py`; public members listed in `__all__` | `_`-prefixed modules and names; `test*` modules are test-runner internals | `__main__.py`, run from the import root as `python -m <package>` | Python Language Reference, The import system (regular packages); Python Library Reference, `__main__` | governance-core folder-architecture check: entry presence and source-root containment, `__all__` declared once, complete and bound, `_` or `test` module names, launcher limited to imports and one guarded delegation to its entry, cross-package deep imports; member-level privacy stays manual review |

- A language absent from this table MUST declare its native packaged-folder mechanism and witness in the project architecture record before use; adopting it in the governance source adds a row here.
- A declared source root is a code-free directory directly below its import base (the directory `python -m <root>.<package>` runs from) that only contains packaged folders; it exposes no public entrypoint and is declared by the project architecture record.
- A root launcher, a code file directly in a repository root outside every declared source root, is a custom entry-file exception: it MUST only delegate to one packaged folder's public entry, launch adaptation stays an FP-21 adapter, and it is permitted only when the project architecture record declares it with `<!-- governance-core-root-launcher: <file> -->` beside the user decision and its re-evaluation trigger; the folder-architecture check accepts exactly the declared Python files and reports each one as a re-evaluation warning.

## Code-size review

code_decomposition_review_lines: 400

- A code file above this line count triggers a decomposition review; it is not a hard cap.

## Runtime path

- Runtime code MUST run exactly one current-contract path per responsibility; an unsupported or failed path ends as an explicit failure or skip with its reason, after cleanup only, never substitute execution.
