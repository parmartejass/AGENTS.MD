---
doc_type: policy
ssot_owner: docs/agents/interfaces/os-processes/os-processes.md
update_trigger: subprocess bounds, owned-process lifecycle, or termination constraints change
---

# OS Processes

Jurisdiction: subprocess bounds, owned-process lifecycle, containment-scoped termination, and terminal cleanup outcomes.

## Baseline
```yaml
baseline:
  interface: "the operating system's process API used directly, with OS containment per owned process at creation: a Windows job object with kill-on-job-close or a POSIX session or process group"
  pattern: "own what you start, contain it at creation, identify it by PID plus start time, bounded waits, verified exit, containment-scoped forced termination only after verified graceful-stop failure, cleanup in finally, terminal cleanup outcome"
  reason: "the process table is the only authority on what is running, and only the OS containment object covers descendants; a PID kill reaps one process and orphans its tree"
  exception: "PID-scoped termination alone only where the platform provides no containment object, Recorded with the orphan risk accepted"
```

## Resource safety
- Waits and termination MUST follow the explicit declared lifecycle contract, and every lifecycle and cleanup wait MUST be time-bounded.
- Cleanup MUST run in a context manager or `finally`.

## Subprocess
- Captured output MUST be bounded.
- A timeout or non-zero exit MUST Return an explicit failed outcome with the reason.
- A bounded wait MUST kill and then reap the child when the bound expires; a timeout path that does not reap after killing is prohibited.
- `shell=True` is prohibited for owned processes; the executable MUST be launched by a validated path with an argument list so the captured PID is the tool's, not a shell's.

## Owned processes
- Process exit MUST be verified after a graceful stop.
- An owned process MUST be identified by PID plus its start time, captured before first use; liveness and termination checks MUST use that identity, never bare PID existence.
- An owned process MUST be placed in its containment object at creation; on Windows it MUST be created suspended and assigned to the job before it resumes.
- `CREATE_NEW_PROCESS_GROUP` is a console-signal mechanism and MUST NOT be recorded as containment.
- Forced termination MUST target the containment object holding only the validated owned PID within a bounded timeout.
- Forced termination is permitted only after verified graceful-stop failure.
- Killing all processes of a kind instead of the validated owned PID is prohibited.
- Attached or user-owned processes MUST NOT be terminated without proven and recorded ownership.
- Unprovable ownership MUST Return terminal `FAILED` or `SKIPPED + reason`.

## Witnesses

| Witness | Meaning |
|---|---|
| `pid_before` | identity check (PID plus start time) before cleanup |
| `pid_after` | identity check (PID plus start time) after cleanup |
| `owned_pid` | captured PID of the workflow-started process |
| `contained_children_before` | descendant count inside the containment object before cleanup |
| `contained_children_after` | descendant count inside the containment object after cleanup; MUST be zero |
| `forced_termination_used` | yes/no with reason and PID |
| `cleanup_result` | success, `FAILED_CLEANUP`, or equivalent terminal outcome |
