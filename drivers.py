"""Driver Center: instala drivers MTK / Qualcomm / Samsung / ADB con 1 clic."""
import os
import subprocess
import threading
import webbrowser

import customtkinter as ctk

from app import config
from app.core import adb, downloader, remote, system_info
from app.core.store import get_app_dir


def build_page(parent, ctx):
    root = ctk.CTkFrame(parent, fg_color="transparent")
    root.pack(fill="both", expand=True)

    head = ctk.CTkFrame(root, fg_color="transparent")
    head.pack(fill="x", padx=12, pady=(10, 4))
    ctk.CTkLabel(head, text="🔧 Driver Center", font=("Arial", 22, "bold")).pack(side="left")
    ctk.CTkButton(head, text="🔄 Volver a detectar", width=160,
                  command=lambda: threading.Thread(target=lambda: _refresh(ctx, state),
                                                   daemon=True).start()).pack(side="right")

    state = {"det": {}, "rows": [], "frame": None, "progress": None, "log": None}

    state["frame"] = ctk.CTkScrollableFrame(root, fg_color="transparent")
    state["frame"].pack(fill="both", expand=True, padx=6)

    state["progress"] = ctk.CTkProgressBar(root, height=14)
    state["progress"].pack(fill="x", padx=14, pady=(6, 2))
    state["progress"].set(0)
    state["log"] = ctk.CTkTextbox(root, height=90, font=("Consolas", 11))
    state["log"].pack(fill="x", padx=14, pady=(2, 10))
    _log(state, "Pulsa 'Volver a detectar' para verificar tus drivers…")
    threading.Thread(target=lambda: _refresh(ctx, state), daemon=True).start()
    return root


def _log(state, msg):
    box = state["log"]
    try:
        box.configure(state="normal")
        box.insert("end", msg + "\n")
        box.see("end")
    except Exception:
        pass


def _set_progress(state, done, total):
    try:
        state["progress"].set((done / total) if total else 0)
    except Exception:
        pass


def _refresh(ctx, state):
    ctx.status("Detectando drivers instalados…")
    state["det"] = system_info.detect_drivers()
    state["det"]["platform-tools"] = adb.platform_tools_ready()
    use_remote = ctx.settings.get("remote_updates", True)
    drivers = remote.get_catalog("drivers", use_remote=use_remote)
    try:
        for w in state["frame"].winfo_children():
            w.destroy()
        state["rows"] = []
        for d in drivers:
            _row(ctx, state, d)
        ctx.status("Drivers verificados. ✅")
    except Exception:
        pass


def _status_text(d, det):
    key = (d.get("detect") or [None])[0]
    if d["id"] == "platform-tools":
        return ("✅ Instalado" if det.get("platform-tools") else "❌ No instalado",
                "#2ECC71" if det.get("platform-tools") else "#E74C3C")
    val = det.get(key) if key else None
    if val is True:
        return "✅ Detectado", "#2ECC71"
    if val is False:
        return "❌ Falta", "#E74C3C"
    return "❔ Sin verificar", "gray"


def _row(ctx, state, d):
    det = state["det"]
    f = ctk.CTkFrame(state["frame"], corner_radius=12)
    f.pack(fill="x", padx=8, pady=6)
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=12, pady=(10, 2))
    ctk.CTkLabel(top, text=d["name"], font=("Arial", 15, "bold")).pack(side="left")
    txt, color = _status_text(d, det)
    ctk.CTkLabel(top, text=txt, font=("Arial", 13, "bold"), text_color=color).pack(side="right")
    ctk.CTkLabel(f, text=d.get("desc", ""), font=("Arial", 12), text_color="gray",
                 wraplength=720, justify="left").pack(anchor="w", padx=12)
    if d.get("size"):
        ctk.CTkLabel(f, text=f"📦 Tamaño: {d['size']}", font=("Arial", 11),
                     text_color="gray").pack(anchor="w", padx=12)
    btns = ctk.CTkFrame(f, fg_color="transparent")
    btns.pack(fill="x", padx=12, pady=8)
    t = d.get("type")
    if t in ("auto", "direct_zip", "direct_exe"):
        ctk.CTkButton(btns, text="⬇ Descargar e instalar", width=200,
                      command=lambda dd=d: threading.Thread(
                          target=lambda: _install(ctx, state, dd), daemon=True).start()
                      ).pack(side="left", padx=(0, 8))
    if d.get("page_url"):
        ctk.CTkButton(btns, text="🌐 Página oficial", width=160,
                      command=lambda u=d["page_url"]: webbrowser.open(u)).pack(side="left", padx=(0, 8))
    for m in d.get("mirrors", []) or []:
        ctk.CTkButton(btns, text=f"🔗 {m['label']}", width=160, fg_color="#3B3B3B",
                      command=lambda u=m["url"]: webbrowser.open(u)).pack(side="left", padx=(0, 8))
    if d.get("notes"):
        ctk.CTkLabel(f, text=f"💡 {d['notes']}", font=("Arial", 11), text_color="#F5B041",
                     wraplength=720, justify="left").pack(anchor="w", padx=12, pady=(0, 10))


def _install(ctx, state, d):
    try:
        ctx.status(f"Instalando {d['name']}…")
        _log(state, f"▶ {d['name']}…")
        cache = os.path.join(get_app_dir(), "cache")
        if d["id"] == "platform-tools":
            adb.ensure_platform_tools(progress=lambda a, b: _set_progress(state, a, b))
            _log(state, "✅ Platform-Tools listo (ADB + Fastboot).")
        elif d["type"] == "direct_zip":
            zipp = os.path.join(cache, d["id"] + ".zip")
            downloader.download(d["url"], zipp, progress=lambda a, b: _set_progress(state, a, b))
            dest = os.path.join(get_app_dir(), "bin", d["id"])
            downloader.extract_zip(zipp, dest, progress=lambda a, b: _set_progress(state, a, b))
            _log(state, f"✅ Descargado en: {dest}")
            _log(state, "💡 " + d.get("notes", ""))
        elif d["type"] == "direct_exe":
            exep = os.path.join(cache, d["id"] + ".exe")
            downloader.download(d["url"], exep, progress=lambda a, b: _set_progress(state, a, b))
            _log(state, f"✅ Ejecutando instalador: {exep}")
            subprocess.Popen([exep], shell=False)
        _set_progress(state, 1, 1)
        ctx.status(f"{d['name']} completado. ✅")
        _refresh(ctx, state)
    except Exception as e:
        ctx.status("Error en la instalación.")
        _log(state, f"❌ Error: {e}")
