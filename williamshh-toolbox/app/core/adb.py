"""ADB / Fastboot real: auto-descarga platform-tools y ejecuta comandos."""
import os
import subprocess

from app.config import PLATFORM_TOOLS_URL
from app.core.downloader import download, extract_zip
from app.core.store import get_app_dir

EXE = "adb.exe" if os.name == "nt" else "adb"
FBEXE = "fastboot.exe" if os.name == "nt" else "fastboot"


def bin_dir():
    d = os.path.join(get_app_dir(), "bin", "platform-tools")
    os.makedirs(d, exist_ok=True)
    return d


def adb_path():
    exe = os.path.join(bin_dir(), EXE)
    return exe if os.path.isfile(exe) else None


def fastboot_path():
    exe = os.path.join(bin_dir(), FBEXE)
    return exe if os.path.isfile(exe) else None


def platform_tools_ready():
    return bool(adb_path())


def ensure_platform_tools(progress=None):
    """Descarga y prepara platform-tools oficiales si faltan. Devuelve ruta de adb."""
    if platform_tools_ready():
        return adb_path()
    cache = os.path.join(get_app_dir(), "cache")
    os.makedirs(cache, exist_ok=True)
    zipp = os.path.join(cache, "platform-tools.zip")
    download(PLATFORM_TOOLS_URL, zipp, progress=progress)
    extract_zip(zipp, os.path.join(get_app_dir(), "bin"))
    if os.name != "nt":
        for exe in (adb_path(), fastboot_path()):
            if exe:
                os.chmod(exe, 0o755)
    if not platform_tools_ready():
        raise RuntimeError("No se pudo preparar platform-tools.")
    return adb_path()


def _run(exe, args, timeout=25):
    flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
    try:
        p = subprocess.run([exe] + args, capture_output=True, text=True,
                           timeout=timeout, creationflags=flags)
        return p.returncode == 0, (p.stdout + p.stderr).strip()
    except FileNotFoundError:
        return False, f"No encontrado: {exe}"
    except subprocess.TimeoutExpired:
        return False, "Tiempo agotado esperando respuesta."


def adb(args, timeout=25):
    return _run(adb_path() or "adb", args, timeout)


def fastboot(args, timeout=25):
    return _run(fastboot_path() or "fastboot", args, timeout)


def parse_adb_devices(output):
    devs = []
    for line in (output or "").splitlines():
        line = line.strip()
        if not line or line.startswith("List of") or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            devs.append((parts[0], parts[1]))
    return devs


def parse_fastboot_devices(output):
    devs = []
    for line in (output or "").splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and parts[1] == "fastboot":
            devs.append((parts[0], "fastboot"))
    return devs


def list_adb_devices():
    ok, out = adb(["devices"])
    return parse_adb_devices(out) if ok else []


def list_fastboot_devices():
    ok, out = fastboot(["devices"])
    return parse_fastboot_devices(out) if ok else []


PROPS = {
    "Marca": "ro.product.brand",
    "Modelo": "ro.product.model",
    "Android": "ro.build.version.release",
    "Compilación": "ro.build.display.id",
    "Bootloader": "ro.bootloader",
}


def device_info(serial=None):
    base = ["-s", serial] if serial else []
    info = {}
    for label, prop in PROPS.items():
        ok, out = adb(base + ["shell", "getprop", prop])
        info[label] = out.strip() if ok and out.strip() else "—"
    return info


REBOOT_MODES = {
    "system": None, "recovery": "recovery", "bootloader": "bootloader",
    "fastboot": "fastboot", "edl": "edl", "download": "download", "sideload": "sideload",
}


def reboot(mode, serial=None):
    base = ["-s", serial] if serial else []
    target = REBOOT_MODES.get(mode)
    if target is None:
        return adb(base + ["reboot"])
    return adb(base + ["reboot", target])


def kill_server():
    return adb(["kill-server"])


def start_server():
    return adb(["start-server"])
