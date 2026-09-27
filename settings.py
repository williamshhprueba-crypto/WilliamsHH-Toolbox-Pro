"""Ajustes + Acerca de + actualizaciones."""
import os
import subprocess
import threading
import webbrowser

import customtkinter as ctk

from app import config
from app.core import remote
from app.core.store import get_app_dir


def build_page(parent, ctx):
    root = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    root.pack(fill="both", expand=True)

    ctk.CTkLabel(root, text="⚙ Ajustes", font=("Arial", 22, "bold")).pack(anchor="w", padx=8, pady=(10, 4))

    f = ctk.CTkFrame(root, corner_radius=12)
    f.pack(fill="x", padx=10, pady=6)
    ctk.CTkLabel(f, text="🎨 Apariencia", font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
    theme = ctk.CTkOptionMenu(f, values=["dark", "light"],
                              command=lambda v: _theme(ctx, v))
    theme.set(ctx.settings.get("theme", "dark"))
    theme.pack(anchor="w", padx=12, pady=(0, 10))

    u = ctk.CTkFrame(root, corner_radius=12)
    u.pack(fill="x", padx=10, pady=6)
    ctk.CTkLabel(u, text="🔄 Actualizaciones", font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
    sw = ctk.CTkSwitch(u, text="Actualizar catálogo desde internet (recomendado)",
                       command=lambda: ctx.settings.set("remote_updates", bool(sw.get())))
    if ctx.settings.get("remote_updates", True):
        sw.select()
    sw.pack(anchor="w", padx=12, pady=4)
    ctk.CTkButton(u, text="🔍 Buscar actualización de la app ahora", width=280,
                  command=lambda: threading.Thread(target=lambda: _check(ctx),
                                                   daemon=True).start()).pack(anchor="w", padx=12, pady=(0, 10))

    d = ctk.CTkFrame(root, corner_radius=12)
    d.pack(fill="x", padx=10, pady=6)
    ctk.CTkLabel(d, text="📁 Datos", font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
    row = ctk.CTkFrame(d, fg_color="transparent")
    row.pack(fill="x", padx=8, pady=(0, 10))
    ctk.CTkButton(row, text="Abrir carpeta de datos", width=200,
                  command=lambda: _open(get_app_dir())).pack(side="left", padx=4)
    ctk.CTkButton(row, text="Restablecer ajustes", width=200, fg_color="#7B7B7B",
                  command=lambda: (ctx.settings.reset(), ctx.status("Ajustes restablecidos."))).pack(side="left", padx=4)

    a = ctk.CTkFrame(root, corner_radius=12)
    a.pack(fill="x", padx=10, pady=6)
    ctk.CTkLabel(a, text=f"ℹ {config.APP_NAME} v{config.VERSION}", font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
    ctk.CTkLabel(a, text=f"{config.TAGLINE}\nHecha con 💪 por {config.AUTHOR} para técnicos y suscriptores.\nUso educativo. Úsala solo en equipos de tu propiedad.",
                 font=("Arial", 12), text_color="gray", justify="left").pack(anchor="w", padx=12)
    row2 = ctk.CTkFrame(a, fg_color="transparent")
    row2.pack(fill="x", padx=8, pady=10)
    ctk.CTkButton(row2, text="▶ YouTube", width=140, fg_color="#C0392B",
                  command=lambda: webbrowser.open(config.YOUTUBE_HANDLE)).pack(side="left", padx=4)
    ctk.CTkButton(row2, text="💬 Telegram", width=140,
                  command=lambda: webbrowser.open(config.TELEGRAM)).pack(side="left", padx=4)
    ctk.CTkButton(row2, text="💽 Playlist Herramientas", width=200, fg_color="#3B3B3B",
                  command=lambda: webbrowser.open(config.PLAYLIST_TOOLS)).pack(side="left", padx=4)
    return root


def _theme(ctx, v):
    ctk.set_appearance_mode(v)
    ctx.settings.set("theme", v)
    ctx.status(f"Tema: {v}")


def _open(path):
    try:
        if os.name == "nt":
            os.startfile(path)  # noqa
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


def _check(ctx):
    ctx.status("Buscando actualización…")
    info = remote.check_update(config.VERSION, use_remote=ctx.settings.get("remote_updates", True))
    win = ctk.CTkToplevel()
    win.title("Actualización")
    win.geometry("440x220")
    if info:
        ctk.CTkLabel(win, text=f"🎉 Nueva versión disponible: {info.get('version')}",
                     font=("Arial", 14, "bold")).pack(padx=14, pady=(14, 4))
        ctk.CTkLabel(win, text=str(info.get("notes", ""))[:300],
                     wraplength=400, justify="left").pack(padx=14)
        if info.get("url"):
            ctk.CTkButton(win, text="⬇ Descargar",
                          command=lambda: webbrowser.open(info["url"])).pack(pady=12)
        ctx.status(f"Disponible v{info.get('version')}.")
    else:
        ctk.CTkLabel(win, text="✅ Tienes la última versión.", font=("Arial", 14, "bold")).pack(pady=30)
        ctx.status("Sin actualizaciones.")
