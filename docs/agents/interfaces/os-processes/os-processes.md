---
doc_type: policy
ssot_owner: docs/agents/interfaces/os-processes/os-processes.md
update_trigger: OS process baseline, containment, or termination platform facts change
---

# OS Processes

Jurisdiction: subprocess bounds, owned-process containment, and termination.

## Baseline
```yaml
baseline:
  interface: "the operating system's process API used directly, with OS containment per owned process at creation: a Windows job object with kill-on-job-close or a POSIX session or process group"
  pattern: "own what you start, contain it at creation, identify it by PID plus start time, bounded waits, verified exit, containment-scoped forced termination only after verified graceful-stop failure, terminal cleanup outcome"
  reason: "the process table is the only authority on what is running, and only the OS containment object covers descendants; a PID kill reaps one process and orphans its tree"
  exception: "PID-scoped termination alone only where the platform provides no containment object, Recorded with the orphan risk accepted"
```

## Processes
- Every lifecycle and cleanup wait MUST be time-bounded.
- Owned processes MUST be cleaned up on every exit path.
- Captured output MUST be bounded.
- An expired wait MUST kill and then reap the child.
- The captured PID MUST be the launched program's, never an intermediate shell's.
- Process exit MUST be verified after a graceful stop.
- Owned-process identity is PID plus start time; bare PID existence proves nothing.
- On Windows a process MUST be created suspended and assigned to its job before it resumes.
- `CREATE_NEW_PROCESS_GROUP` is a console-signal mechanism, not containment.
- Forced termination MUST target only the containment object of the validated owned process.
- Attached or user-owned processes MUST NOT be terminated without proven ownership.
- Cleanup MUST leave zero processes in the containment object.
