import os
import sys
import time
import subprocess
import ctypes
import platform
import io
from typing import Dict, Any, List, Optional
from PIL import ImageGrab

def get_system_stats() -> Dict[str, Any]:
    """Retrieve host PC metrics: CPU %, Memory, Disk space, and Uptime."""
    stats: Dict[str, Any] = {
        "platform": f"{platform.system()} {platform.release()}",
        "cpu_percent": 0.0,
        "memory_total": 0,
        "memory_used": 0,
        "memory_free": 0,
        "memory_percent": 0.0,
        "uptime_seconds": 0,
        "hostname": platform.node()
    }
    
    # Try using psutil if available
    try:
        import psutil
        stats["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        stats["memory_total"] = mem.total
        stats["memory_used"] = mem.used
        stats["memory_free"] = mem.available
        stats["memory_percent"] = mem.percent
        stats["uptime_seconds"] = int(time.time() - psutil.boot_time())
        return stats
    except ImportError:
        pass
        
    # Windows native fallback via ctypes
    if platform.system() == "Windows":
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ('dwLength', ctypes.c_ulong),
                    ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong),
                    ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong),
                    ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                stats["memory_total"] = stat.ullTotalPhys
                stats["memory_free"] = stat.ullAvailPhys
                stats["memory_used"] = stat.ullTotalPhys - stat.ullAvailPhys
                stats["memory_percent"] = float(stat.dwMemoryLoad)

            uptime_ms = ctypes.windll.kernel32.GetTickCount64()
            stats["uptime_seconds"] = int(uptime_ms / 1000)
        except Exception:
            pass

    return stats


def execute_power_command(action: str) -> Dict[str, Any]:
    """Execute host PC power actions: shutdown, restart, sleep, lock."""
    action = action.lower().strip()
    system_os = platform.system()

    if action == "lock":
        if system_os == "Windows":
            ctypes.windll.user32.LockWorkStation()
            return {"success": True, "message": "Host workstation locked successfully"}
        else:
            return {"success": False, "message": "Lock is only supported on Windows"}

    elif action == "sleep":
        if system_os == "Windows":
            subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
            return {"success": True, "message": "Host system entering sleep mode"}
        else:
            return {"success": False, "message": "Sleep is only supported on Windows"}

    elif action == "restart":
        if system_os == "Windows":
            subprocess.Popen(["shutdown", "/r", "/t", "5", "/c", "MyWalt Remote Restart Request"])
            return {"success": True, "message": "Host system restarting in 5 seconds"}
        else:
            subprocess.Popen(["shutdown", "-r", "+1"])
            return {"success": True, "message": "Host system restarting"}

    elif action == "shutdown":
        if system_os == "Windows":
            subprocess.Popen(["shutdown", "/s", "/t", "5", "/c", "MyWalt Remote Shutdown Request"])
            return {"success": True, "message": "Host system shutting down in 5 seconds"}
        else:
            subprocess.Popen(["shutdown", "-h", "+1"])
            return {"success": True, "message": "Host system shutting down"}

    else:
        return {"success": False, "message": f"Unknown action: {action}"}


def run_terminal_command(command: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
    """Execute a PowerShell or CMD shell command safely and return output."""
    if not command or not command.strip():
        return {"stdout": "", "stderr": "Empty command", "returncode": -1}

    if not cwd or not os.path.exists(cwd):
        cwd = os.path.expanduser("~")

    try:
        if platform.system() == "Windows":
            cmd_args = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command]
        else:
            cmd_args = ["/bin/bash", "-c", command]

        proc = subprocess.run(
            cmd_args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
            "cwd": cwd
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds.",
            "returncode": -1,
            "cwd": cwd
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "returncode": -1,
            "cwd": cwd
        }

# --- REAL-TIME REMOTE DESKTOP & MOUSE / KEYBOARD CONTROL ---

def get_desktop_frame(quality: int = 50, scale_width: int = 1280) -> bytes:
    """Capture host desktop screen as compressed JPEG bytes."""
    img = ImageGrab.grab()
    if img.width > scale_width:
        ratio = scale_width / float(img.width)
        new_height = int(img.height * ratio)
        img = img.resize((scale_width, new_height))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def remote_mouse_event(action: str, rel_x: float = 0.5, rel_y: float = 0.5, button: str = "left", delta: int = 0) -> Dict[str, Any]:
    """Execute remote mouse move, click, right-click, double-click, or scroll on host PC."""
    if platform.system() != "Windows":
        return {"success": False, "message": "Mouse control is only supported on Windows"}
        
    user32 = ctypes.windll.user32
    screen_w = user32.GetSystemMetrics(0) # SM_CXSCREEN
    screen_h = user32.GetSystemMetrics(1) # SM_CYSCREEN
    
    target_x = max(0, min(screen_w - 1, int(rel_x * screen_w)))
    target_y = max(0, min(screen_h - 1, int(rel_y * screen_h)))
    
    user32.SetCursorPos(target_x, target_y)
    
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_WHEEL = 0x0800

    if action == "click":
        if button == "right":
            user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        else:
            user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif action == "dblclick":
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.04)
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    elif action == "rightclick":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    elif action == "scroll":
        user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        
    return {"success": True, "x": target_x, "y": target_y}


def remote_keyboard_event(key: Optional[str] = None, text: Optional[str] = None, shortcut: Optional[str] = None) -> Dict[str, Any]:
    """Execute remote single keypress, typed text, or keyboard shortcut on host PC."""
    if platform.system() != "Windows":
        return {"success": False, "message": "Keyboard control is only supported on Windows"}

    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002

    VK_MAP = {
        "backspace": 0x08, "tab": 0x09, "enter": 0x0D, "shift": 0x10, "ctrl": 0x11,
        "alt": 0x12, "esc": 0x1B, "space": 0x20, "pageup": 0x21, "pagedown": 0x22,
        "end": 0x23, "home": 0x24, "left": 0x25, "up": 0x26, "right": 0x27,
        "down": 0x28, "delete": 0x2E, "win": 0x5B
    }

    if shortcut:
        sc = shortcut.lower().strip()
        if sc == "win+d":
            user32.keybd_event(0x5B, 0, 0, 0)
            user32.keybd_event(ord('D'), 0, 0, 0)
            user32.keybd_event(ord('D'), 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(0x5B, 0, KEYEVENTF_KEYUP, 0)
        elif sc == "win+e":
            user32.keybd_event(0x5B, 0, 0, 0)
            user32.keybd_event(ord('E'), 0, 0, 0)
            user32.keybd_event(ord('E'), 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(0x5B, 0, KEYEVENTF_KEYUP, 0)
        elif sc == "win+r":
            user32.keybd_event(0x5B, 0, 0, 0)
            user32.keybd_event(ord('R'), 0, 0, 0)
            user32.keybd_event(ord('R'), 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(0x5B, 0, KEYEVENTF_KEYUP, 0)
        elif sc == "alt+tab":
            user32.keybd_event(0x12, 0, 0, 0)
            user32.keybd_event(0x09, 0, 0, 0)
            user32.keybd_event(0x09, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(0x12, 0, KEYEVENTF_KEYUP, 0)
        elif sc == "ctrl+c":
            user32.keybd_event(0x11, 0, 0, 0)
            user32.keybd_event(ord('C'), 0, 0, 0)
            user32.keybd_event(ord('C'), 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)
        elif sc == "ctrl+v":
            user32.keybd_event(0x11, 0, 0, 0)
            user32.keybd_event(ord('V'), 0, 0, 0)
            user32.keybd_event(ord('V'), 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)

    elif text:
        for char in text:
            vk = user32.VkKeyScanW(ord(char))
            if vk != -1:
                need_shift = (vk & 0x0100) != 0
                vk_code = vk & 0xFF
                if need_shift:
                    user32.keybd_event(0x10, 0, 0, 0)
                user32.keybd_event(vk_code, 0, 0, 0)
                user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
                if need_shift:
                    user32.keybd_event(0x10, 0, KEYEVENTF_KEYUP, 0)

    elif key:
        k = key.lower()
        if k in VK_MAP:
            vk = VK_MAP[k]
            user32.keybd_event(vk, 0, 0, 0)
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        elif len(k) == 1:
            vk = user32.VkKeyScanW(ord(k))
            vk_code = vk & 0xFF
            user32.keybd_event(vk_code, 0, 0, 0)
            user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

    return {"success": True}
