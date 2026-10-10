# SPEC.md — Project Specification

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: Requirements confirmed and locked.

## Vision
Transform MyWalt into a high-performance, secure remote PC file manager by offloading intensive file system operations (recursive space analysis, directory scanning, multi-item batch operations, and searching) to a native C++ engine, while introducing strict Write-Protection authorization gates so that modifying, creating, saving, renaming, uploading, or deleting files requires explicit Master Password verification and authorization.

## Goals
1. **High-Performance C++ Native Engine** — Provide a C++ native engine (`native/native_engine.cpp`) with CLI and JSON output for fast directory listing, recursive space analysis, filename/fulltext search, and batch operations, with automated Python bridging and graceful fallback in `backend/file_ops.py`.
2. **File Modification Write-Protection Gate** — Restrict all file modification endpoints (`save`, `delete`, `rename`, `create`, `copy`, `move`, `upload`, `compress`, `extract`) behind a Write Access verification gate requiring the Master Password.
3. **Interactive UI Access Lock & Authorization Modal** — Provide an intuitive UI lock badge in the navigation header (🔒 Read-Only / 🔓 Write Access) and an interactive Authorization Modal that prompts for the Master Password before executing any file modification.
4. **Seamless Session Security** — Issue time-limited write access tokens with automatic renewal and manual revoke capabilities.

## Non-Goals (Out of Scope)
- Rewriting the entire HTTP/HTML web server stack in C++ (FastAPI remains the web gateway, maximizing cross-platform stability and ease of running).
- Modifying OS-level file system ACLs directly or bypassing Windows kernel permissions.

## Constraints
- Windows 10/11 environment with Device Guard policy restrictions on MSYS2 binaries; native C++ code must be clean, standard C++17 with MSVC / GCC build configuration and provide robust Python fallback if binaries cannot run.
- Zero breaking changes to existing endpoints or frontend UI aesthetics.
- Strict GSD commit discipline: one task per commit, verified with empirical proof.

## Success Criteria
- [x] `.gsd/SPEC.md` marked `FINALIZED`.
- [ ] `native/native_engine.cpp` implements directory scanning, recursive space analysis, search, and batch operations.
- [ ] `backend/file_ops.py` bridges calls to the C++ engine with transparent fallback.
- [ ] `backend/security.py` and `main.py` enforce Write Access tokens on all write operations.
- [ ] Unauthorized write requests return HTTP 403 with `WRITE_ACCESS_REQUIRED`.
- [ ] Frontend displays Write Lock state and prompts with an Authorization Modal on attempted file modification.
- [ ] Verified with empirical test results and git commits.

---

*Last updated: 2026-10-10*
