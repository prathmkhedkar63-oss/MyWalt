import os
import sys
import subprocess
import json
import mimetypes
import io
import zipfile
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, Response, HTTPException, Depends, Cookie, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.security import (
    verify_master_password,
    set_master_password,
    has_master_password,
    create_token,
    verify_token,
    sanitize_path,
    is_ip_locked,
    record_failed_attempt,
    reset_failed_attempts
)
from backend.file_ops import (
    get_drive_letters,
    get_user_shortcuts,
    list_directory,
    read_text_file,
    save_text_file,
    create_item,
    rename_item,
    delete_items,
    move_items,
    copy_items,
    create_zip_archive,
    extract_archive,
    analyze_directory_space,
    load_favorites,
    save_favorites,
    search_file_contents
)
from backend.system import (
    get_system_stats,
    execute_power_command,
    run_terminal_command,
    get_desktop_frame,
    remote_mouse_event,
    remote_keyboard_event
)

app = FastAPI(title="MyWalt Remote File Access", version="2.0.0")

# Setup CORS for local network access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
NATIVE_SEARCH_EXE = os.path.join(BASE_DIR, "native", "fast_search.exe")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

# Security Middleware for Response Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Auth dependency
async def get_current_user(request: Request, session_token: Optional[str] = Cookie(None), token: Optional[str] = Query(None)):
    t = token or session_token
    if not t:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            t = auth_header.split(" ")[1]
            
    if not t:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    payload = verify_token(t)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
        
    return payload


# Pydantic Schemas
class LoginRequest(BaseModel):
    password: str

class PasswordChangeRequest(BaseModel):
    old_password: Optional[str] = None
    new_password: str

class CreateItemRequest(BaseModel):
    target_dir: str
    name: str
    is_directory: bool = False

class RenameRequest(BaseModel):
    path: str
    new_name: str

class DeleteRequest(BaseModel):
    paths: List[str]
    soft_delete: bool = True

class TransferRequest(BaseModel):
    sources: List[str]
    dest_dir: str

class SaveFileRequest(BaseModel):
    path: str
    content: str

class CompressRequest(BaseModel):
    sources: List[str]
    target_dir: str
    archive_name: str

class ExtractRequest(BaseModel):
    archive_path: str
    dest_dir: str

class PowerRequest(BaseModel):
    action: str

class TerminalRequest(BaseModel):
    command: str
    cwd: Optional[str] = None

class FavoritesRequest(BaseModel):
    favorites: List[Dict[str, str]]

class RemoteMouseRequest(BaseModel):
    action: str
    rel_x: float = 0.5
    rel_y: float = 0.5
    button: str = "left"
    delta: int = 0

class RemoteKeyboardRequest(BaseModel):
    key: Optional[str] = None
    text: Optional[str] = None
    shortcut: Optional[str] = None

# Endpoints
@app.post("/api/login")
async def login(req: LoginRequest, request: Request, response: Response):
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    if is_ip_locked(client_ip):
        raise HTTPException(status_code=429, detail="Too many failed login attempts. IP temporarily locked for 15 minutes.")
        
    if verify_master_password(req.password):
        reset_failed_attempts(client_ip)
        token = create_token({"user": "admin"})
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            samesite="lax",
            max_age=86400 * 7
        )
        return {"success": True, "token": token}
    else:
        record_failed_attempt(client_ip)
        raise HTTPException(status_code=401, detail="Incorrect password")

@app.post("/api/logout")
async def logout(response: Response):
    response.delete_cookie("session_token")
    return {"success": True}

@app.get("/api/status")
async def status(request: Request, session_token: Optional[str] = Cookie(None)):
    token = session_token or (request.headers.get("Authorization") or "").replace("Bearer ", "")
    is_authenticated = verify_token(token) is not None
    return {
        "status": "online",
        "has_master_password": has_master_password(),
        "is_authenticated": is_authenticated
    }

@app.post("/api/set-password")
async def update_password(req: PasswordChangeRequest, user=Depends(get_current_user)):
    if has_master_password() and req.old_password:
        if not verify_master_password(req.old_password):
            raise HTTPException(status_code=400, detail="Current password incorrect")
    set_master_password(req.new_password)
    return {"success": True, "message": "Master password updated successfully"}

@app.get("/api/drives")
async def get_drives(user=Depends(get_current_user)):
    return get_drive_letters()

@app.get("/api/shortcuts")
async def get_shortcuts(user=Depends(get_current_user)):
    return get_user_shortcuts()

@app.get("/api/files")
async def list_files(path: Optional[str] = Query(None), user=Depends(get_current_user)):
    target = path
    if not target or target.strip() == "":
        drives = get_drive_letters()
        target = drives[0]["path"] if drives else os.getcwd()
        
    safe_p = sanitize_path(target)
    if not safe_p:
        raise HTTPException(status_code=403, detail="Access denied or invalid path")
        
    try:
        data = list_directory(safe_p)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/download")
async def download_file(path: str = Query(...), user=Depends(get_current_user)):
    safe_p = sanitize_path(path)
    if not safe_p or not os.path.isfile(safe_p):
        raise HTTPException(status_code=404, detail="File not found or access denied")
    return FileResponse(safe_p, filename=os.path.basename(safe_p))

@app.get("/api/stream")
async def stream_media(path: str = Query(...), request: Request = None, user=Depends(get_current_user)):
    """Stream audio/video with HTTP Range header support for seeking."""
    safe_p = sanitize_path(path)
    if not safe_p or not os.path.isfile(safe_p):
        raise HTTPException(status_code=404, detail="Media file not found")
        
    file_size = os.path.getsize(safe_p)
    range_header = request.headers.get("range") if request else None
    
    mime_type, _ = mimetypes.guess_type(safe_p)
    if not mime_type:
        mime_type = "video/mp4" if safe_p.endswith((".mp4", ".mkv", ".mov", ".webm")) else "application/octet-stream"

    if range_header:
        try:
            byte_str = range_header.replace("bytes=", "")
            start_str, end_str = byte_str.split("-")
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1
        except Exception:
            start = 0
            end = file_size - 1

        if start >= file_size or end >= file_size:
            return Response(status_code=416, headers={"Content-Range": f"bytes */{file_size}"})

        chunk_size = (end - start) + 1
        def iter_file():
            with open(safe_p, "rb") as f:
                f.seek(start)
                bytes_left = chunk_size
                while bytes_left > 0:
                    read_bytes = min(1024 * 1024, bytes_left)
                    data = f.read(read_bytes)
                    if not data:
                        break
                    bytes_left -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": mime_type,
        }
        return StreamingResponse(iter_file(), status_code=206, headers=headers)
    else:
        return FileResponse(safe_p, media_type=mime_type)

@app.get("/api/pdf/render")
async def render_pdf(path: str = Query(...), user=Depends(get_current_user)):
    """Render PDF document in browser."""
    safe_p = sanitize_path(path)
    if not safe_p or not os.path.isfile(safe_p):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(safe_p, media_type="application/pdf", headers={"Content-Disposition": "inline"})

@app.post("/api/upload")
async def upload_files(
    target_dir: str = Form(...),
    files: List[UploadFile] = File(...),
    user=Depends(get_current_user)
):
    safe_dir = sanitize_path(target_dir)
    if not safe_dir or not os.path.isdir(safe_dir):
        raise HTTPException(status_code=400, detail="Invalid destination directory")
        
    uploaded, errors = [], []
    for f in files:
        try:
            dest_file = os.path.join(safe_dir, f.filename)
            with open(dest_file, "wb") as buffer:
                while content := await f.read(1024 * 1024):
                    buffer.write(content)
            uploaded.append(f.filename)
        except Exception as e:
            errors.append(f"{f.filename}: {str(e)}")
            
    return {"uploaded": uploaded, "errors": errors}

@app.post("/api/create")
async def create_new_item(req: CreateItemRequest, user=Depends(get_current_user)):
    safe_dir = sanitize_path(req.target_dir)
    if not safe_dir:
        raise HTTPException(status_code=403, detail="Invalid path")
    try:
        res = create_item(safe_dir, req.name, req.is_directory)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/rename")
async def rename(req: RenameRequest, user=Depends(get_current_user)):
    safe_p = sanitize_path(req.path)
    if not safe_p:
        raise HTTPException(status_code=403, detail="Invalid path")
    try:
        res = rename_item(safe_p, req.new_name)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/delete")
async def delete(req: DeleteRequest, user=Depends(get_current_user)):
    sanitized_paths = []
    for p in req.paths:
        sp = sanitize_path(p)
        if sp:
            sanitized_paths.append(sp)
    res = delete_items(sanitized_paths, soft_delete=req.soft_delete)
    return res

@app.post("/api/copy")
async def copy(req: TransferRequest, user=Depends(get_current_user)):
    safe_dest = sanitize_path(req.dest_dir)
    if not safe_dest:
        raise HTTPException(status_code=403, detail="Invalid destination path")
    sources = [sp for p in req.sources if (sp := sanitize_path(p))]
    return copy_items(sources, safe_dest)

@app.post("/api/move")
async def move(req: TransferRequest, user=Depends(get_current_user)):
    safe_dest = sanitize_path(req.dest_dir)
    if not safe_dest:
        raise HTTPException(status_code=403, detail="Invalid destination path")
    sources = [sp for p in req.sources if (sp := sanitize_path(p))]
    return move_items(sources, safe_dest)

@app.get("/api/read")
async def read_file(path: str = Query(...), user=Depends(get_current_user)):
    safe_p = sanitize_path(path)
    if not safe_p:
        raise HTTPException(status_code=403, detail="Invalid path")
    try:
        res = read_text_file(safe_p)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/save")
async def save_file(req: SaveFileRequest, user=Depends(get_current_user)):
    safe_p = sanitize_path(req.path)
    if not safe_p:
        raise HTTPException(status_code=403, detail="Invalid path")
    try:
        res = save_text_file(safe_p, req.content)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- ARCHIVES & ZIP STREAMING ---
@app.post("/api/archive/compress")
async def compress(req: CompressRequest, user=Depends(get_current_user)):
    safe_dir = sanitize_path(req.target_dir)
    if not safe_dir:
        raise HTTPException(status_code=403, detail="Invalid target directory")
    sources = [sp for p in req.sources if (sp := sanitize_path(p))]
    try:
        return create_zip_archive(sources, safe_dir, req.archive_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/archive/extract")
async def extract(req: ExtractRequest, user=Depends(get_current_user)):
    safe_archive = sanitize_path(req.archive_path)
    safe_dest = sanitize_path(req.dest_dir)
    if not safe_archive or not safe_dest:
        raise HTTPException(status_code=403, detail="Invalid paths")
    try:
        return extract_archive(safe_archive, safe_dest)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/archive/download-zip")
async def download_as_zip(path: str = Query(...), user=Depends(get_current_user)):
    safe_p = sanitize_path(path)
    if not safe_p or not os.path.exists(safe_p):
        raise HTTPException(status_code=404, detail="Path not found")

    folder_name = os.path.basename(safe_p.rstrip("/\\")) or "archive"
    zip_filename = f"{folder_name}.zip"

    def zip_stream_generator():
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isfile(safe_p):
                zf.write(safe_p, os.path.basename(safe_p))
            else:
                for root, _, files in os.walk(safe_p):
                    for f in files:
                        full_f = os.path.join(root, f)
                        rel_f = os.path.relpath(full_f, safe_p)
                        zf.write(full_f, rel_f)
        buf.seek(0)
        yield buf.getvalue()

    return StreamingResponse(
        zip_stream_generator(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
    )

# --- SYSTEM MONITORING & POWER CONTROLS ---
@app.get("/api/system/stats")
async def system_stats(user=Depends(get_current_user)):
    return get_system_stats()

@app.post("/api/system/power")
async def system_power(req: PowerRequest, user=Depends(get_current_user)):
    return execute_power_command(req.action)

@app.post("/api/system/terminal")
async def system_terminal(req: TerminalRequest, user=Depends(get_current_user)):
    return run_terminal_command(req.command, req.cwd)

# --- REAL-TIME REMOTE DESKTOP & MOUSE / KEYBOARD CONTROL ---
@app.get("/api/remote/desktop/frame")
async def desktop_frame(quality: int = Query(50), width: int = Query(1280), user=Depends(get_current_user)):
    try:
        frame_bytes = get_desktop_frame(quality=quality, scale_width=width)
        return Response(content=frame_bytes, media_type="image/jpeg", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/remote/mouse")
async def remote_mouse(req: RemoteMouseRequest, user=Depends(get_current_user)):
    return remote_mouse_event(req.action, req.rel_x, req.rel_y, req.button, req.delta)

@app.post("/api/remote/keyboard")
async def remote_keyboard(req: RemoteKeyboardRequest, user=Depends(get_current_user)):
    return remote_keyboard_event(req.key, req.text, req.shortcut)

# --- STORAGE ANALYZER & FAVORITES ---
@app.get("/api/storage/analyze")
async def analyze_storage(path: str = Query(...), user=Depends(get_current_user)):
    safe_p = sanitize_path(path)
    if not safe_p:
        raise HTTPException(status_code=403, detail="Invalid path")
    try:
        return analyze_directory_space(safe_p)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/favorites")
async def get_favs(user=Depends(get_current_user)):
    return load_favorites()

@app.post("/api/favorites")
async def update_favs(req: FavoritesRequest, user=Depends(get_current_user)):
    save_favorites(req.favorites)
    return {"success": True, "favorites": req.favorites}

# --- SEARCH ---
@app.get("/api/search")
async def search_files(
    root: str = Query(...),
    q: str = Query(...),
    max_results: int = Query(100),
    user=Depends(get_current_user)
):
    safe_root = sanitize_path(root)
    if not safe_root or not os.path.exists(safe_root):
        raise HTTPException(status_code=400, detail="Invalid root path")
        
    if not os.path.exists(NATIVE_SEARCH_EXE):
        # Fallback to python search if native binary is missing
        return {"results": search_file_contents(safe_root, q, max_results)}
        
    try:
        cmd = [NATIVE_SEARCH_EXE, safe_root, q, str(max_results)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if proc.returncode == 0:
            return json.loads(proc.stdout)
        else:
            return {"error": proc.stderr, "results": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/search/fulltext")
async def fulltext_search(
    root: str = Query(...),
    q: str = Query(...),
    max_results: int = Query(100),
    user=Depends(get_current_user)
):
    safe_root = sanitize_path(root)
    if not safe_root or not os.path.exists(safe_root):
        raise HTTPException(status_code=400, detail="Invalid root path")
    return {"results": search_file_contents(safe_root, q, max_results)}

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
async def root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MyWalt Remote File Access Server Running</h1>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
