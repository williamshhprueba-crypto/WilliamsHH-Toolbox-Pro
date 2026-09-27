"""Info del sistema + detección REAL de drivers con pnputil (Win10/11)."""
import os
import platform
import subprocess


def is_windows():
    return os.name == "nt"


def is_admin():
    if not is_windows():
        try:
            return os.geteuid() == 0
        except Exception:
            return False
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def os_name():
    return platform.platform()


def run_quiet(args, timeout=30):
    flags = 0x08000000 if os.name == "nt" else 0
    try:
        p = subprocess.run(args, capture_output=True, text=True,
                           timeout=timeout, creationflags=flags)
        return p.returncode == 0, ((p.stdout or "") + (p.stderr or "")).strip()
    except Exception as e:
        return False, str(e)


def detect_drivers():
    """Detecta drivers instalados. None = no se pudo verificar."""
    res = {"samsung": None, "mediatek": None, "qualcomm": None, "android": None}
    if not is_windows():
        return res
    ok, out = run_quiet(["pnputil", "/enum-drivers"])
    if not ok:
        return res
    low = out.lower()
    res["samsung"] = "samsung" in low
    res["mediatek"] = any(k in low for k in ("mediatek", "mtk", "preloader", "vcom", "0e8d"))
    res["qualcomm"] = any(k in low for k in ("qdloader", "qualcomm", "9008", "qusb"))
    res["android"] = any(k in low for k in ("android", "adb interface", "fastboot", "google"))
    return res


def list_ports():
    ok, out = run_quiet(["pnputil", "/enum-devices", "/class", "Ports"])
    return out if ok else "No se pudo leer puertos (solo Windows 10/11)."


def kill_process(name):
    if is_windows():
        return run_quiet(["taskkill", "/F", "/IM", name])
    return run_quiet(["pkill", "-f", name])
