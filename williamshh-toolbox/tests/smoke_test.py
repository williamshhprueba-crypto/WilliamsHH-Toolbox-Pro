"""Prueba de humo: valida datos + núcleo sin abrir ventanas."""
import json
import os
import sys
import tempfile
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

fails = []


def check(name, cond, extra=""):
    print(("✅ " if cond else "❌ ") + name + (f" ({extra})" if extra and not cond else ""))
    if not cond:
        fails.append(name)


# 1. JSONs válidos
for fname in ("drivers.json", "tools.json", "tutorials.json", "links.json"):
    p = os.path.join(ROOT, "app", "data", fname)
    try:
        data = json.load(open(p, encoding="utf-8"))
        check(f"JSON válido: {fname}", isinstance(data, (list, dict)))
    except Exception as e:
        check(f"JSON válido: {fname}", False, e)

tools = json.load(open(os.path.join(ROOT, "app", "data", "tools.json"), encoding="utf-8"))
drivers = json.load(open(os.path.join(ROOT, "app", "data", "drivers.json"), encoding="utf-8"))
tuts = json.load(open(os.path.join(ROOT, "app", "data", "tutorials.json"), encoding="utf-8"))

# 2. URLs bien formadas (sin links inventados rotos)
for t in tools:
    for k in ("download_url", "page_url", "tutorial_url"):
        u = t.get(k)
        if u:
            check(f"URL {t['id']}.{k}", u.startswith("http"), u)
for d in drivers:
    for k in ("url", "page_url"):
        u = d.get(k)
        if u:
            check(f"URL driver {d['id']}.{k}", u.startswith("http"), u)
    for m in d.get("mirrors", []) or []:
        check(f"URL mirror {d['id']}", m["url"].startswith("http"), m["url"])

# 3. IDs de YouTube válidos (11 caracteres)
bad = [v for v in tuts if len(v.get("id", "")) != 11]
check(f"Tutoriales con ID válido ({len(tuts)} videos)", not bad, bad[:3])

# 4. Núcleo
from app import config  # noqa: E402
from app.core import downloader, adb, system_info, remote, store  # noqa: E402
check("config.VERSION", bool(config.VERSION))
check("resource_path existe", os.path.isfile(config.resource_path("data", "tools.json")))
check("parse adb devices", adb.parse_adb_devices("List of devices\nABC123\tdevice\n") == [("ABC123", "device")])
check("parse fastboot", adb.parse_fastboot_devices("XYZ\tfastboot\n") == [("XYZ", "fastboot")])
check("get_app_dir", os.path.isdir(store.get_app_dir()))
check("remote fallback local", isinstance(remote.get_catalog("tools", use_remote=False), list))

# 5. Descargador: zip local
tmp = tempfile.mkdtemp()
zp = os.path.join(tmp, "t.zip")
with zipfile.ZipFile(zp, "w") as z:
    z.writestr("hola.txt", "ok")
downloader.extract_zip(zp, os.path.join(tmp, "out"))
check("extract_zip", open(os.path.join(tmp, "out", "hola.txt")).read() == "ok")
check("sha256", len(downloader.sha256_of(zp)) == 64)
check("system_info", isinstance(system_info.detect_drivers(), dict))

# 6. Módulos UI importan (sin abrir ventana)
try:
    import customtkinter  # noqa: F401
    from app.modules import home, drivers as mdrv, devices, library, tutorials, pcfix, settings  # noqa: F401
    import app.main  # noqa: F401
    check("imports UI + main", True)
except ImportError as e:
    check("imports UI + main", False, f"{e} (instala requirements)")

print()
if fails:
    print(f"💥 {len(fails)} FALLOS: {fails}")
    sys.exit(1)
print("🎉 TODO OK — la Toolbox está lista.")
