Common edge cases AI-generated code misses in file I/O:

## Resource Management
- **Not closing files on error paths** — `try/finally` or context managers (`with`) omitted, especially in complex control flow
- **Partial writes** — assuming `write()` writes all bytes; it may return a short count on some systems/interfaces
- **Forgetting to flush** — data stuck in buffers never reaches disk before process exit or crash

## Filesystem State
- **TOCTOU races** — checking `os.path.exists()` then opening; another process can create/delete in between
- **Symlink attacks** — following symlinks to unintended locations, especially with user-controlled paths
- **Concurrent access** — no file locking when multiple processes/threads read-modify-write the same file
- **Directory doesn't exist** — assuming the parent directory of the output path exists

## Encoding & Content
- **Text vs binary mode** — opening in text mode (`"r"`) when file contains binary data, or vice versa
- **BOM handling** — UTF-8 with BOM (`\xef\xbb\xbf`) causing parse failures
- **Line ending inconsistency** — `\r\n` vs `\n` causing off-by-one or corrupt output on cross-platform code
- **Null bytes** — not handling `\x00` in filenames or content

## Error Handling
- **Swallowing `EINTR`** — interrupted system calls not retried (matters in C/low-level code)
- **Disk full** — `ENOSPC` not handled; partial file left on disk without cleanup
- **Permission errors at write time** — file opened for write but flush/close raises the permission error, not open
- **Stale file handles** — file deleted or replaced externally while handle is open

## Atomicity
- **Non-atomic updates** — writing directly to the target file instead of write-to-temp + rename, leaving a window where readers see a partial file
- **Truncation without rewrite** — opening with `"w"` truncates immediately; if the subsequent write fails, the original content is gone

## Platform Differences
- **Path separator assumptions** — hardcoding `/` instead of `os.path.join()` or `pathlib`
- **Case sensitivity** — `File.txt` ≠ `file.txt` on Linux, `==` on macOS/Windows by default
- **Max path length** — Windows `MAX_PATH` = 260 chars without long path opt-in

The most consistently missed are **disk-full handling**, **atomic writes**, and **TOCTOU races** — they don't show up in normal testing and require deliberate fault injection to catch.