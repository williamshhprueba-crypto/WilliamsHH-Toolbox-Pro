"""PC Fix: utilidades para técnicos (ADB colgado, puertos, guías)."""
import os
import shutil
import subprocess
import threading
import webbrowser

import customtkinter as ctk

from app.core import adb, system_info
from app.core.store import get_app_dir


def build_page(parent, ctx):
    root = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    root.pack(fill="both", expand=True)
    state = {"log": None}

    ctk.CTkLabel(root, text="🩺 PC Fix para Técnicos", font=("Arial", 22, "bold")).pack(anchor="w", padx=8, pady=(10, 2))
    if not system_info.is_admin():
        ctk.CTkLabel(root, text="⚠️ No ejecutas como Administrador: algunas funciones necesitan admin.",
                     font=("Arial", 12), text_color="#F5B041").pack(anchor="w", padx=8)

    _section(root, "🔌 ADB / Conexión", [
        ("🧹 Matar ADB colgado", lambda: _do(ctx, state, _kill_adb)),
        ("🔄 Reiniciar servidor ADB", lambda: _do(ctx, state, _restart_adb)),
        ("🔎 Ver puertos COM", lambda: _do(ctx, state, _ports)),
    ])
    _section(root, "🪟 Windows", [
        ("🧰 Abrir Administrador de dispositivos", lambda: _do(ctx, state, _devmgmt)),
        ("📁 Abrir carpeta de la Toolbox", lambda: _do(ctx, state, _open_dir)),
        ("🗑 Limpiar caché de descargas", lambda: _do(ctx, state, _clean)),
    ])
    _section(root, "📖 Guías", [
        ("📝 Instalar drivers sin firma (MTK/QC)", lambda: _guide(ctx)),
        ("▶ Canal de YouTube", lambda: webbrowser.open("https://www.youtube.com/@WilliamsHH-v3e")),
    ])

    state["log"] = ctk.CTkTextbox(root, height=180, font=("Consolas", 11))
    state["log"].pack(fill="x", padx=10, pady=10)
    state["log"].insert("end", f"Sistema: {system_info.os_name()}\nListo.\n")
    return root


def _section(parent, title, buttons):
    f = ctk.CTkFrame(parent, corner_radius=12)
    f.pack(fill="x", padx=10, pady=6)
    ctk.CTkLabel(f, text=title, font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(8, 4))
    row = ctk.CTkFrame(f, fg_color="transparent")
    row.pack(fill="x", padx=8, pady=(0, 10))
    for label, cmd in buttons:
        ctk.CTkButton(row, text=label, command=cmd).pack(side="left", padx=5)


def _log(state, msg):
    try:
        state["log"].insert("end", msg + "\n")
        state["log"].see("end")
    except Exception:
        pass


def _do(ctx, state, fn):
    threading.Thread(target=lambda: fn(ctx, state), daemon=True).start()


def _kill_adb(ctx, state):
    ok, out = system_info.kill_process("adb.exe" if os.name == "nt" else "adb")
    _log(state, f"🧹 ADB terminado. {out[:200]}")
    ctx.status("ADB terminado.")


def _restart_adb(ctx, state):
    adb.kill_server()
    ok, out = adb.start_server()
    _log(state, f"🔄 Servidor ADB reiniciado. {out[:200]}")
    ctx.status("ADB reiniciado.")


def _ports(ctx, state):
    _log(state, "🔎 Puertos:\n" + system_info.list_ports()[:1500])
    ctx.status("Puertos listados.")


def _devmgmt(ctx, state):
    try:
        if os.name == "nt":
            subprocess.Popen(["devmgmt.msc"], shell=True)
        _log(state, "🧰 Administrador de dispositivos abierto.")
    except Exception as e:
        _log(state, f"❌ {e}")


def _open_dir(ctx, state):
    d = get_app_dir()
    try:
        if os.name == "nt":
            os.startfile(d)  # noqa
        else:
            subprocess.Popen(["xdg-open", d])
        _log(state, f"📁 {d}")
    except Exception as e:
        _log(state, f"❌ {e}")


def _clean(ctx, state):
    cache = os.path.join(get_app_dir(), "cache")
    try:
        if os.path.isdir(cache):
            shutil.rmtree(cache)
        os.makedirs(cache, exist_ok=True)
        _log(state, "🗑 Caché limpiada.")
        ctx.status("Caché limpiada.")
    except Exception as e:
        _log(state, f"❌ {e}")


def _guide(ctx):
    win = ctk.CTkToplevel()
    win.title("Instalar drivers sin firma digital")
    win.geometry("560x420")
    txt = ctk.CTkTextbox(win, font=("Arial", 12))
    txt.pack(fill="both", expand=True, padx=12, pady=12)
    txt.insert("end",
        "📝 INSTALAR DRIVERS MTK / QUALCOMM SIN FIRMA (Windows 10/11)\n\n"
        "1️⃣ Abre Configuración → Recuperación → Inicio avanzado → Reiniciar ahora.\n\n"
        "2️⃣ Solucionar problemas → Opciones avanzadas → Configuración de inicio → Reiniciar.\n\n"
        "3️⃣ Pulsa 7 o F7 (Deshabilitar el uso obligatorio de controladores firmados).\n\n"
        "4️⃣ Al reiniciar, instala tu driver MTK / QDLoader 9008 normal.\n\n"
        "5️⃣ Conecta el equipo apagado (EDL: Vol+ y Vol- juntos, o punto test).\n\n"
        "⚠️ Al próximo reinicio Windows vuelve a modo seguro. Repite si reinstalas.\n")
    txt.configure(state="disabled")
