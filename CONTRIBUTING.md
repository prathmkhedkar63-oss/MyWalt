# Contributing to MyWalt

Thank you for your interest in contributing to **MyWalt**! We welcome contributions, bug reports, feature requests, and security improvements.

## 🚀 Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/MyWalt.git
   cd MyWalt
   ```
3. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Development Guidelines

- **Code Style**: Follow PEP 8 guidelines for Python code.
- **Security**: Security is paramount. Do not weaken path sanitization (`sanitize_path`), JWT verification, or rate-limiting functions.
- **Pull Requests**:
  1. Create a descriptive topic branch (`git checkout -b feature/amazing-feature`).
  2. Commit your changes (`git commit -m "Add amazing feature"`).
  3. Push to the branch (`git push origin feature/amazing-feature`).
  4. Open a Pull Request on GitHub.

## 🛡️ Reporting Security Vulnerabilities

If you discover a security vulnerability within MyWalt, please open a confidential disclosure issue or email the maintainer directly. Do not disclose vulnerabilities in public issues before a fix is released.

Thank you for helping build a safe, fast, and feature-rich remote file management tool!
