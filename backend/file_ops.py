import os
import shutil
import time
import platform
import string
import json
import zipfile
import tarfile
import ctypes
from typing import List, Dict, Any, Optional


def get_drive_letters() -> List[Dict[str, Any]]:
    """Enumerate available drives (Windows) or root (Linux/Mac)."""
    drives = []
    if platform.system() == "Windows":
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            if os.path.exists(drive_path):
                total, used, free = 0, 0, 0
                try:
                    usage = shutil.disk_usage(drive_path)
                    total = usage.total
                    used = usage.used
                    free = usage.free
                except Exception:
                    pass
                drives.append({
                    "name": f"Local Disk ({letter}:)",
                    "path": drive_path,
                    "total": total,
                    "used": used,
                    "free": free,
                    "is_dir": True,
                })
    else:
        try:
            usage = shutil.disk_usage("/")
            drives.append({
                "name": "Root (/)",
                "path": "/",
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "is_dir": True,
            })
        except Exception:
            drives.append({"name": "Root (/)", "path": "/", "total": 0, "used": 0, "free": 0, "is_dir": True})
    return drives


def get_user_shortcuts() -> List[Dict[str, str]]:
    """Get common user folder shortcuts (Desktop, Documents, Downloads, Pictures, Videos) with real paths."""
    user_home = os.path.expanduser("~")
    shortcuts = []
    for name in ["Desktop", "Documents", "Downloads", "Pictures", "Videos"]:
        p = os.path.join(user_home, name)
        if os.path.exists(p):
            shortcuts.append({"name": name, "path": p})
    return shortcuts


def get_file_category(filename: str, is_dir: bool) -> str:
    """Classify a file by extension into a UI-friendly category."""
    if is_dir:
        return "folder"
    ext = os.path.splitext(filename)[1].lower()
    MAP = {
        "code":     {".py",".cpp",".c",".h",".hpp",".js",".html",".css",".json",".ts",
                     ".jsx",".tsx",".md",".java",".cs",".php",".sh",".bat",".ps1",
                     ".txt",".yaml",".yml",".xml",".ini",".conf",".env",".rs",".go",
                     ".rb",".swift",".kt",".lua",".r",".sql",".toml",".log"},
        "image":    {".png",".jpg",".jpeg",".gif",".svg",".webp",".bmp",".ico",".tiff"},
        "video":    {".mp4",".mkv",".webm",".avi",".mov",".flv",".wmv"},
        "audio":    {".mp3",".wav",".ogg",".flac",".m4a",".aac",".wma"},
        "archive":  {".zip",".tar",".gz",".7z",".rar",".bz2",".xz"},
        "document": {".pdf",".docx",".doc",".xlsx",".xls",".pptx",".ppt",".odt",".csv"},
    }
    for cat, exts in MAP.items():
        if ext in exts:
            return cat
    return "file"


def list_directory(target_path: str) -> Dict[str, Any]:
    """List all items in a directory with metadata."""
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Path does not exist: {target_path}")
    if not os.path.isdir(target_path):
        raise NotADirectoryError(f"Not a directory: {target_path}")

    items: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        entries = list(os.scandir(target_path))
    except PermissionError:
        raise PermissionError(f"Access denied: {target_path}")

    for entry in entries:
        try:
            is_dir = entry.is_dir(follow_symlinks=False)
            stat = entry.stat(follow_symlinks=False)
            items.append({
                "name": entry.name,
                "path": os.path.abspath(entry.path),
                "is_dir": is_dir,
                "size": stat.st_size if not is_dir else 0,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "category": get_file_category(entry.name, is_dir),
            })
        except Exception as e:
            errors.append(f"{entry.name}: {e}")

    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

    # Build breadcrumbs
    norm = os.path.abspath(target_path)
    crumbs: List[Dict[str, str]] = []
    drive, tail = os.path.splitdrive(norm)
    if drive:
        crumbs.append({"name": f"{drive}\\", "path": f"{drive}\\"})
        cur = f"{drive}\\"
        for part in [p for p in tail.split(os.sep) if p]:
            cur = os.path.join(cur, part)
            crumbs.append({"name": part, "path": cur})
    else:
        crumbs.append({"name": "/", "path": "/"})
        cur = "/"
        for part in [p for p in norm.split(os.sep) if p]:
            cur = os.path.join(cur, part)
            crumbs.append({"name": part, "path": cur})

    return {
        "current_path": norm,
        "breadcrumbs": crumbs,
        "items": items,
        "count": len(items),
        "errors": errors,
    }


def read_text_file(file_path: str, max_size_mb: int = 10) -> Dict[str, Any]:
    """Read a text file for the in-browser editor."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    size = os.path.getsize(file_path)
    if size > max_size_mb * 1024 * 1024:
        raise ValueError(f"File too large ({size/(1024*1024):.1f} MB)")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return {"content": f.read(), "encoding": "utf-8", "size": size}
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return {"content": f.read(), "encoding": "latin-1", "size": size}


def save_text_file(file_path: str, content: str) -> Dict[str, Any]:
    """Save content to a text file."""
    parent = os.path.dirname(file_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"success": True, "size": os.path.getsize(file_path)}


def create_item(target_dir: str, name: str, is_directory: bool) -> Dict[str, Any]:
    """Create a new file or folder."""
    full = os.path.join(target_dir, name)
    if os.path.exists(full):
        raise FileExistsError(f"'{name}' already exists")
    if is_directory:
        os.makedirs(full, exist_ok=True)
    else:
        with open(full, "w", encoding="utf-8") as f:
            f.write("")
    return {"success": True, "path": full}


def rename_item(src_path: str, new_name: str) -> Dict[str, Any]:
    """Rename a file or folder."""
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    dest = os.path.join(os.path.dirname(src_path), new_name)
    if os.path.exists(dest):
        raise FileExistsError(f"'{new_name}' already exists")
    os.rename(src_path, dest)
    return {"success": True, "new_path": dest}


def send_to_recycle_bin(path: str) -> bool:
    """Move file/folder to Windows Recycle Bin via Win32 API."""
    if platform.system() == "Windows":
        try:
            class SHFILEOPSTRUCTW(ctypes.Structure):
                _fields_ = [
                    ("hwnd", ctypes.c_void_p),
                    ("wFunc", ctypes.c_uint),
                    ("pFrom", ctypes.c_wchar_p),
                    ("pTo", ctypes.c_wchar_p),
                    ("fFlags", ctypes.c_ushort),
                    ("fAnyOperationsAborted", ctypes.c_bool),
                    ("hNameMappings", ctypes.c_void_p),
                    ("lpszProgressTitle", ctypes.c_wchar_p)
                ]
            FO_DELETE = 3
            FOF_ALLOWUNDO = 0x0040
            FOF_NOCONFIRMATION = 0x0010
            FOF_SILENT = 0x0004

            p_from = os.path.abspath(path) + "\0\0"
            fileop = SHFILEOPSTRUCTW()
            fileop.wFunc = FO_DELETE
            fileop.pFrom = p_from
            fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
            res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(fileop))
            return res == 0
        except Exception:
            pass
    return False


def delete_items(paths: List[str], soft_delete: bool = True) -> Dict[str, Any]:
    """Delete one or more files/folders (soft delete to Recycle Bin by default)."""
    deleted, failed = [], []
    for p in paths:
        try:
            if soft_delete and send_to_recycle_bin(p):
                deleted.append(p)
                continue
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
            deleted.append(p)
        except Exception as e:
            failed.append({"path": p, "error": str(e)})
    return {"deleted": deleted, "failed": failed}


def move_items(sources: List[str], dest_dir: str) -> Dict[str, Any]:
    """Move files/folders to a destination directory."""
    if not os.path.isdir(dest_dir):
        raise NotADirectoryError(dest_dir)
    moved, failed = [], []
    for src in sources:
        try:
            shutil.move(src, dest_dir)
            moved.append(src)
        except Exception as e:
            failed.append({"path": src, "error": str(e)})
    return {"moved": moved, "failed": failed}


def copy_items(sources: List[str], dest_dir: str) -> Dict[str, Any]:
    """Copy files/folders to a destination directory."""
    if not os.path.isdir(dest_dir):
        raise NotADirectoryError(dest_dir)
    copied, failed = [], []
    for src in sources:
        try:
            name = os.path.basename(src)
            target = os.path.join(dest_dir, name)
            if os.path.isdir(src):
                shutil.copytree(src, target, dirs_exist_ok=True)
            else:
                shutil.copy2(src, target)
            copied.append(src)
        except Exception as e:
            failed.append({"path": src, "error": str(e)})
    return {"copied": copied, "failed": failed}


# --- NEW FEATURES: ARCHIVES, FAVORITES, SPACE ANALYZER, FULL-TEXT SEARCH ---

FAVORITES_FILE = os.path.join(os.path.dirname(__file__), ".favorites.json")

def load_favorites() -> List[Dict[str, str]]:
    """Load saved favorite pinned folders."""
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_favorites(favorites: List[Dict[str, str]]) -> bool:
    """Save favorite pinned folders."""
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(favorites, f, indent=2)
        return True
    except Exception:
        return False


def create_zip_archive(sources: List[str], target_dir: str, archive_name: str) -> Dict[str, Any]:
    """Compress multiple files/folders into a .zip archive."""
    if not archive_name.endswith(".zip"):
        archive_name += ".zip"
    zip_path = os.path.join(target_dir, archive_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src in sources:
            if not os.path.exists(src):
                continue
            if os.path.isfile(src):
                zf.write(src, os.path.basename(src))
            elif os.path.isdir(src):
                base_dir = os.path.basename(src)
                for root, _, files in os.walk(src):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.join(base_dir, os.path.relpath(full_path, src))
                        zf.write(full_path, rel_path)
                        
    return {"success": True, "archive_path": zip_path, "size": os.path.getsize(zip_path)}


def extract_archive(archive_path: str, dest_dir: str) -> Dict[str, Any]:
    """Extract .zip, .tar, .tar.gz archives."""
    if not os.path.exists(archive_path):
        raise FileNotFoundError(archive_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(dest_dir)
        return {"success": True, "dest_dir": dest_dir}
    elif tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(dest_dir)
        return {"success": True, "dest_dir": dest_dir}
    else:
        raise ValueError("Unsupported archive format. Supports .zip and .tar archives.")


def analyze_directory_space(target_path: str) -> Dict[str, Any]:
    """Calculate space breakdown by subfolders and top largest files."""
    if not os.path.exists(target_path) or not os.path.isdir(target_path):
        raise NotADirectoryError(target_path)

    total_size = 0
    subfolders: List[Dict[str, Any]] = []
    top_files: List[Dict[str, Any]] = []

    try:
        entries = list(os.scandir(target_path))
    except Exception as e:
        raise PermissionError(str(e))

    for entry in entries:
        try:
            if entry.is_dir(follow_symlinks=False):
                folder_size = 0
                for root, _, files in os.walk(entry.path):
                    for f in files:
                        try:
                            fp = os.path.join(root, f)
                            folder_size += os.path.getsize(fp)
                        except Exception:
                            pass
                total_size += folder_size
                subfolders.append({
                    "name": entry.name,
                    "path": entry.path,
                    "size": folder_size
                })
            elif entry.is_file(follow_symlinks=False):
                f_size = entry.stat().st_size
                total_size += f_size
                top_files.append({
                    "name": entry.name,
                    "path": entry.path,
                    "size": f_size
                })
        except Exception:
            pass

    subfolders.sort(key=lambda x: x["size"], reverse=True)
    top_files.sort(key=lambda x: x["size"], reverse=True)

    return {
        "target_path": target_path,
        "total_size": total_size,
        "subfolders": subfolders[:15],
        "top_files": top_files[:15]
    }


def search_file_contents(root_path: str, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """Full-text content search across text, code, and markdown files."""
    results: List[Dict[str, Any]] = []
    query_lower = query.lower()
    TEXT_EXTS = {".txt", ".py", ".cpp", ".c", ".h", ".js", ".ts", ".html", ".css", ".json", ".md", ".yaml", ".yml", ".ini", ".conf", ".log", ".bat", ".ps1", ".xml", ".csv"}

    count = 0
    for root, dirs, files in os.walk(root_path):
        # Skip hidden directories like .git, __pycache__, node_modules
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "node_modules", "$Recycle.Bin", "System Volume Information")]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in TEXT_EXTS:
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, 1):
                            if query_lower in line.lower():
                                results.append({
                                    "file_name": file,
                                    "file_path": full_path,
                                    "line_number": line_no,
                                    "snippet": line.strip()[:150]
                                })
                                count += 1
                                if count >= max_results:
                                    return results
                except Exception:
                    pass
    return results
