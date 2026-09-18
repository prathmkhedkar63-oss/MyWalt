import sys
import os
import subprocess
import threading
import time
import re
import uvicorn

# Force UTF-8 stdout encoding for Windows console compatibility
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_cloudflared_executable() -> str:
    local_bin = os.path.join(BASE_DIR, "cloudflared.exe")
    if os.path.exists(local_bin):
        return local_bin
    system_bin = shutil.which("cloudflared")
    if system_bin:
        return system_bin
    return ""

def start_cloudflare_tunnel():
    cf_bin = get_cloudflared_executable()
    if not cf_bin:
        print("[!] Cloudflare executable not found.")
        print("    To enable remote access, install cloudflared (e.g. winget install Cloudflare.cloudflared)")
        print("    or place cloudflared.exe in the project folder.")
        return

    time.sleep(1.5) # Wait for FastAPI server to start
    print("\n[+] Starting Cloudflare Tunnel...")
    
    cmd = [cf_bin, "tunnel", "--url", "http://localhost:8000"]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )
        
        for line in proc.stdout:
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                tunnel_url = match.group(0)
                print("\n" + "="*70)
                print(" [*] CLOUDFLARE REMOTE TUNNEL ACTIVE!")
                print(f" [*] REMOTE SECURE URL: {tunnel_url}")
                print(" [*] Open this URL on your phone/tablet/laptop anywhere!")
                print(" [*] Protected by Master Password (default: admin)")
                print("="*70 + "\n")
                break
    except Exception as e:
        print(f"[!] Cloudflare tunnel error: {e}")

if __name__ == "__main__":
    exe_path = os.path.join(BASE_DIR, "native", "fast_search.exe")
    cpp_path = os.path.join(BASE_DIR, "native", "fast_search.cpp")
    
    if not os.path.exists(exe_path) and os.path.exists(cpp_path):
        print("[+] Compiling native C++ fast search engine...")
        try:
            subprocess.run(["g++", "-O3", "-std=c++17", cpp_path, "-o", exe_path], check=True)
            print("[+] C++ compilation complete!")
        except Exception as e:
            print(f"[!] Warning: C++ compilation failed: {e}")

    enable_tunnel = "--no-tunnel" not in sys.argv

    print("="*60)
    print(" [+] MyWalt Secure Remote PC File Control Server")
    print(" [+] Local Access URL : http://localhost:8000")
    print(" [+] Default Password : admin")
    print("="*60)

    if enable_tunnel:
        threading.Thread(target=start_cloudflare_tunnel, daemon=True).start()

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
