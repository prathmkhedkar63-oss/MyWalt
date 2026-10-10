# 🌐 MyWalt — Remote PC File Manager & Desktop Control Server

**MyWalt** is a high-performance, self-hosted web application that lets you securely access, manage, edit, stream, and search files on your host PC from any phone, tablet, or laptop anywhere in the world — for **free**.

---

## ✨ Features

- 📁 **Complete File Explorer**: Browse drives, search, copy, move, rename, upload, download, and delete files directly in your web browser.
- ⚡ **High-Speed C++ Native Engine**: Includes a high-performance native C++ engine (`native/native_engine.cpp`) and fast search engine (`native/fast_search.cpp`) for instant directory scanning, recursive disk space analysis, batch deletions, and multithreaded searches across millions of files.
- 🔐 **File Modification Write-Protection Gate**: Protects host PC files from unauthorized or accidental changes with an active Write-Access Gate. File modifications (saving, deleting, creating, renaming, uploading, compressing) require explicit Master Password verification and authorization, featuring an interactive Authorization Modal and navbar status lock badge (🔒 Read-Only / 🔓 Write Access).
- 🎬 **Media Streaming & PDF Viewer**: Stream high-definition videos (`.mp4`, `.webm`, `.mkv`) with seeking support, listen to audio files, and view PDFs directly in the browser.
- 📝 **In-Browser Text Editor**: Read and edit code (`.py`, `.js`, `.json`, `.cpp`, `.md`, etc.) and text files with syntax support.
- 📊 **Storage Analyzer**: Visual breakdown of disk space consumption by subfolder and top largest files.
- 🖥️ **Live Remote Desktop & Remote Controls**: Real-time screen frame capture, mouse click/scroll control, and keyboard shortcut emulation.
- 📦 **Zip Compression & Extraction**: Compress folders into `.zip` archives or extract `.zip` and `.tar` archives remotely.
- 🛡️ **Multi-Layer Security**: PBKDF2 master password hashing, JWT session authentication, strict path traversal sanitization, IP lockout after 5 failed login attempts, and OWASP security headers.
- 🌐 **Free Remote Access**: Built-in integration with Cloudflare Tunnels (`cloudflared`), Tailscale, ngrok, and LocalTunnel.

---

## 🏗️ Architecture & Project Structure

```
MyWalt/
├── backend/
│   ├── security.py       # JWT auth, Write Access tokens, PBKDF2 hashing & rate limiter
│   ├── file_ops.py       # Directory listing, file transfers, archives & C++ engine bridge
│   └── system.py         # System metrics, power controls, terminal & remote desktop
├── native/
│   ├── native_engine.cpp # Unified C++ native engine (list, analyze, search, batch ops)
│   ├── fast_search.cpp   # Native C++ search engine
│   ├── build.bat         # Automated build script for MSVC, GCC, and Clang
│   └── CMakeLists.txt    # CMake configuration for native engine binaries
├── static/
│   ├── index.html        # Modern responsive Web UI with Write Access Modal & lock badge
│   ├── app.js            # Frontend logic, API client & Write Access interceptor
│   └── style.css         # Modern glassmorphism, dark-mode & security badge styling
├── main.py               # FastAPI application backend server & protected endpoints
├── run_server.py         # Server launcher with auto-tunneling and C++ compiler
├── REMOTE_ACCESS_GUIDE.md# Instructions for setting up free remote access
├── requirements.txt      # Python dependencies
└── start.bat             # Windows one-click starter script
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites

- **Python**: Python 3.9 or higher
- **G++ Compiler** *(Optional, recommended)*: MinGW or GCC for compiling the native C++ search engine.

### 2. Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/prathmkhedkar63-oss/MyWalt.git
   cd MyWalt
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Running the Server

Start the server using `run_server.py` or double-clicking `start.bat`:

```bash
python run_server.py
```

The server will initialize on `http://localhost:8000`.

- **Default Master Password**: `admin`
- On first login, you will be prompted to set a new custom Master Password.

---

## 🌐 Setting Up Free Remote Access

To control your host PC from any phone or remote device outside your home network, choose one of the following methods:

### Option 1: Cloudflare Tunnel (`cloudflared`) — Recommended ⭐⭐⭐⭐⭐

1. Install Cloudflare CLI:
   ```powershell
   winget install Cloudflare.cloudflared
   ```
2. Start MyWalt with automatic tunneling:
   ```bash
   python run_server.py
   ```
   Or run the tunnel manually:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
3. Open the secure `https://xxx.trycloudflare.com` URL provided in your console on any phone or browser!

For full details on Tailscale, ngrok, and LocalTunnel setups, see [REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md).

---

## 🔒 Security Architecture

- **Path Traversal Shield**: All incoming file path requests are normalized and sanitized using `sanitize_path()` to ensure operations remain bounded.
- **Brute-Force Rate Limiting**: After 5 failed password attempts, the requesting IP address is locked out for 15 minutes.
- **Session Security**: Session tokens are signed using JWT algorithms and sent via `HttpOnly`, `SameSite=Strict` cookies.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome! Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.
