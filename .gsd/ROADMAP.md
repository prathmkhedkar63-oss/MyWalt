# ROADMAP.md — Project Roadmap

## Milestone 1: High-Performance C++ Native Engine & Write-Protection Gate

### Phase 1: High-Performance C++ Native Engine Architecture
- [ ] Task 1.1: Develop comprehensive C++ native engine (`native/native_engine.cpp`) with commands for directory listing, space analysis, search, and batch file operations.
- [ ] Task 1.2: Add build automation (`native/build.bat`, `native/CMakeLists.txt`) and bridge `backend/file_ops.py` to `native_engine` with fallback.

### Phase 2: Backend Write-Protection Gate & Access Tokens
- [ ] Task 2.1: Implement Write Access tokens and verification in `backend/security.py`.
- [ ] Task 2.2: Add `/api/auth/write-access` endpoints and enforce Write Access dependency on all mutating endpoints in `main.py`.

### Phase 3: Frontend UI Write Lock & Authorization Modal
- [ ] Task 3.1: Add navbar Write Lock status badge and Authorization Modal in `static/index.html` & `static/style.css`.
- [ ] Task 3.2: Implement interceptor logic in `static/app.js` to prompt for Master Password when attempting file modifications.

### Phase 4: Verification & Integration Testing
- [ ] Task 4.1: End-to-end API verification of write protection, authorization flows, and native engine fallback.
- [ ] Task 4.2: Final state snapshot and documentation updates.
