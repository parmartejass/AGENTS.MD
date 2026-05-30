---
doc_type: reference
ssot_owner: docs/project/data-truth/data-truth.md
update_trigger: data-truth ownership, provenance, validation, or routing changes
---

# Data Truth

## Purpose
- Record declared project data-truth owners and route consumers to them.
- Allow docs or doc-owned artifacts to own facts only when explicitly declared here or in the referenced owner.
- Prevent duplicate/non-owner copies of values, mappings, defaults, headers, thresholds, paths, or business/source data.

## Record Schema
Each durable data-truth record uses this shape:
- ID: `DT-YYYYMMDD-NNN`
- Status: `active | proposed | deprecated | superseded`
- Truth type: `input-artifact | source-artifact | workbook | schema | config | constant | default | external-system | mapping | threshold | path | sample-data | document-owned`
- Owner SSOT:
- Doc role: `owner | router | provenance | interpretation | validation`
- Scope:
- Statement:
- Provenance:
- Consumers:
- Validation:
- Change rule:
- Related protected behavior:
- Related rules:
- Supersedes:
- Superseded by:
- Last verified:
- Evidence/version:
- Re-verification trigger:

## Records
- No project-owned data truths are currently declared here.

This is an explicit reviewed-empty registry state for project-owned data-truth records in this governance-pack repo.
- Reviewed-empty date: `2026-05-31`
- Evidence: project docs currently route the data-truth authority branch, but no concrete project data/config/constant/default/source-artifact truth has been promoted into this registry.
- Scope: this statement does not claim that no data/config/constants/defaults exist in the repo; it only states that no project-owned data-truth record has been promoted here yet.
- Next update trigger: add `DT-*` records when a concrete project data/config/constant/default/source-artifact authority must affect future behavior.
- Rule: do not add policy records here to satisfy a checker.
