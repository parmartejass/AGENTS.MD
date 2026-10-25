---
doc_type: playbook
ssot_owner: docs/agents/playbooks/packaging/packaging.md
update_trigger: artifact identity, build, signing, inventory, or downgrade rules change
---

# Packaging

Jurisdiction: how the distributable artifact is built from the locked source state, and the version identity, signature, provenance, component inventory, and downgrade rules it carries.

```yaml
baseline:
  interface: one declared build command over the committed lockfile producing the distributable artifact
  pattern: "locked inputs; single build invocation; one version identity stamped into the artifact; timestamped signature; component inventory; artifact recorded in the changelog closure record"
  reason: "one command over locked inputs is the only form in which a build is reproducible and its provenance checkable; it avoids per-machine build recipes and unverifiable artifacts"
  exception: "a developer local build for inspection only, never distributed; Record it as non-release"
```

## Version identity
- The artifact version MUST have exactly one source in the repository.
- The versioning scheme MUST be declared as SemVer or CalVer. A breaking change to a published contract MUST increment the major component.
- A shipped artifact MUST carry a version greater than the previous release, unless a recorded downgrade decision covers it.

## Build
- Embedded build timestamps MUST derive from a recorded source date, not wall-clock time. A release MUST be built from a clean working tree.
- The target platform tags, the minimum interpreter version, and the bundled third-party license set MUST be Recorded with the artifact.

## Signing and provenance
- Every distributed Windows executable and installer MUST be signed with an RFC 3161 timestamp. Each repository MUST record its signing route and its availability constraints.
- A machine-readable component inventory in a declared standard format MUST accompany every release.
- Build provenance MUST record the build platform, source revision, and inputs. Published Python distributions MUST use trusted publishing with attestations where the index supports it.

## Install and downgrade
- An installer MUST declare whether downgrade installation is permitted and Record the flag that permits it.
