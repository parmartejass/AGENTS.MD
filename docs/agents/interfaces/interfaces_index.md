# Interfaces Layer Index

- [excel/excel_index.md](excel/excel_index.md) - Excel workbooks: OOXML-first baseline, data facts, COM constraints. Required when: workbook creation, update, or automation is in scope.
- [pdf/pdf_index.md](pdf/pdf_index.md) - PDF files: deterministic merge baseline and integrity facts. Required when: PDF generation, merge, or integrity validation is in scope.
- [filesystem/filesystem_index.md](filesystem/filesystem_index.md) - Files and folders: atomic durable write baseline and destination safety. Required when: repository or external writes occur.
- [os-processes/os-processes_index.md](os-processes/os-processes_index.md) - Processes: OS containment baseline, subprocess bounds, owned-process termination. Required when: starting, attaching to, or terminating processes.
- [gui-toolkit/gui-toolkit_index.md](gui-toolkit/gui-toolkit_index.md) - Desktop UI runtime: UI-thread baseline and cancellation. Required when: GUI or main-thread updates are involved.
