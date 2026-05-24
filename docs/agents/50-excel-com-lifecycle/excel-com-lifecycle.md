---
doc_type: policy
ssot_owner: AGENTS.md
update_trigger: Excel lifecycle invariants change
---

# 50 - Excel COM Lifecycle (Hard Requirements)

Excel COM automation is stateful and failure-prone; correctness is defined by owned lifecycle, PID-scoped cleanup, and recorded cleanup outcomes.

This policy applies after a workflow has selected or used Excel COM automation, including `Excel.Application`, `win32com`, `xlwings`, `Dispatch`, `DispatchEx`, `CreateObject`, `GetObject`, or `GetActiveObject`. It does not decide when COM should be selected; Excel library/backend selection remains owned by `docs/agents/playbooks/excel-library-selection-playbook/excel-library-selection-playbook.md`.

## Ownership Model

Default to a new workflow-owned Excel automation instance when the workflow needs cleanup authority. The workflow must record the owned Excel PID before opening workflow workbooks.

Attaching to an already-running user Excel instance is allowed only when the task explicitly declares attach-to-user-instance behavior. Attached instances are not workflow-owned by default: do not quit, kill, or blanket-close workbooks in an attached instance unless ownership of that PID and those workbooks is proven and recorded. If ownership cannot be proven, produce terminal `FAILED` or `SKIPPED + reason`.

A separate Excel COM-created process/object model instance is an ownership boundary for lifecycle control; it is not sandbox isolation. Excel instances may still share or contend over user profile state, add-ins, templates, clipboard, printers, file locks, links, cached credentials, macros, dialogs, and other external resources.

Multiple PID operations are required lifecycle witnesses, not duplicate PID authorities: capture establishes ownership, validation prevents killing the wrong process, quit verification proves graceful cleanup, and forced termination is the bounded last-resort cleanup witness.

## Invariants

1. Workflow-owned Excel instances must be closed on workflow exit.
2. Workflow-owned PID must be captured, validated before cleanup, and verified after quit.
3. Shutdown must be time-bounded, including lifecycle and cleanup waits.
4. Forced termination is cleanup-only and allowed only after verified graceful-quit failure and PID validation.
5. Cleanup must be in `finally`, including COM init/uninit pairing on all failure paths.
6. Workflow-owned workbooks and child COM references must be closed/released before application quit/release.
7. Cleanup failures must be recorded as `FAILED_CLEANUP` or an equivalent terminal cleanup outcome; cleanup errors must not be swallowed or reported as success.

## Required Lifecycle Stages

- initialize COM for the current thread when required
- create or attach to Excel and record whether the instance is workflow-owned
- capture and record the owned PID when the instance is workflow-owned
- record workflow-owned workbook identities before processing
- open only declared workflow workbooks
- process
- save/close only workflow-owned workbooks
- release workbook, worksheet/range, and other child COM references before app release
- restore changed Excel application settings in `finally`
- quit Excel gracefully when the instance is workflow-owned
- verify process exit for the owned PID
- if still alive after verified graceful-quit failure: terminate only the validated PID within a bounded timeout
- uninitialize COM for the current thread when initialized by the workflow
- log each stage and final cleanup outcome

## Witnesses

Required run evidence for COM workflows:

- `instance_ownership`: workflow-owned or explicit attach-to-user-instance
- `owned_pid`: captured PID when workflow-owned
- `pid_before` and `pid_after`: process-existence checks around cleanup
- `workbooks_owned`: workflow-owned workbook identities
- `workbooks_closed`: close/save result per workflow-owned workbook
- `settings_restored`: any changed Excel application settings restored or failure recorded
- `com_refs_released`: application/workbook/child reference release outcome
- `quit_called`: graceful quit attempted for workflow-owned instance
- `forced_termination_used`: yes/no with reason and PID when used
- `cleanup_result`: success, `FAILED_CLEANUP`, or equivalent terminal cleanup outcome

## Forbidden Patterns

- leaving workflow-owned `Excel.exe` running intentionally
- using `GetObject` or `GetActiveObject` as the default path for workflows that need cleanup authority
- quitting, killing, or blanket-closing an attached/user Excel instance without proven ownership
- blanket `Workbooks.Close` unless the workflow owns the whole Excel instance and all open workbooks in it
- killing all Excel processes instead of the validated workflow-owned PID
- swallowing COM or cleanup errors without recording and re-raising/propagating the terminal outcome
- reporting success when workbook close, app quit, reference release, COM uninit, or PID cleanup failed
- COM initialization without guaranteed uninitialization on all failure paths
- unbounded waits during open, refresh, save, quit, verify, or cleanup
- allowing macro/security/UI prompts to hang the workflow instead of failing or terminalizing with reason
