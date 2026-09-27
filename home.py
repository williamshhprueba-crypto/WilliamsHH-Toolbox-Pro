"""Página de inicio / panel principal."""
import threading

import customtkinter as ctk

from app import config
from app.core import adb, system_info


def _card(parent, title, value, btn_text=None, btn_cmd=None):
    f = ctk.CTkFrame(parent, corner_radius=12)
    ctk.CTkLabel(f, text=title, font=("Arial", 13, "bold")).pack(anchor="w", padx=14, pady=(10, 0))
    lbl = ctk.CTkLabel(f, text=value, font=("Arial", 22, "bold"), text_color="#FFD34D")
    lbl.pack(anchor="w", padx=14)
    if btn_text:
        ctk.CTkButton(f, text=btn_text, command=btn_cmd, height=30).pack(anchor="w", padx=14, pady=(4, 12))
    else:
        ctk.CTkLabel(f, text="").pack(pady=(0, 8))
    return f, lbl


def build_page(parent, ctx):
    root = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    root.pack(fill="both", expand=True)

    ctk.CTkLabel(root, text=f"👋 Bienvenido a {config.APP_NAME}",
                 font=("Arial", 24, "bold")).pack(anchor="w", padx=8, pady=(6, 0))
    ctk.CTkLabel(root, text=f"{config.TAGLINE}  •  v{config.VERSION}  •  por {config.AUTHOR}",
                 font=("Arial", 13), text_color="gray").pack(anchor="w", padx=8, pady=(0, 12))

    stats = ctk.CTkFrame(root, fg_color="transparent")
    stats.pack(fill="x", padx=4)
    for i in range(4):
        stats.grid_columnconfigure(i, weight=1)

    pt_txt = "✅ Listo" if adb.platform_tools_ready() else "❌ Falta"
    c1, lbl_pt = _card(stats, "Platform-Tools (ADB)", pt_txt, "Instalar ahora",
                       lambda: threading.Thread(target=_install_pt,
                                                args=(ctx, lbl_pt), daemon=True).start())
    c1.grid(row=0, column=0, padx=6, sticky="ew")
    admin_txt = "✅ Sí" if system_info.is_admin() else "⚠️ No"
    c2, _ = _card(stats, "Admin", admin_txt)
    c2.grid(row=0, column=1, padx=6, sticky="ew")
    c3, lbl_dev = _card(stats, "Dispositivos", "—", "Detectar",
                        lambda: threading.Thread(target=_detect,
                                                 args=(ctx, lbl_dev), daemon=True).start())
    c3.grid(row=0, column=2, padx=6, sticky="ew")
    c4, _ = _card(stats, "Tutoriales", "30+", "Ver videos", lambda: ctx.goto("tutorials"))
    c4.grid(row=0, column=3, padx=6, sticky="ew")

    qa = ctk.CTkFrame(root, corner_radius=12)
    qa.pack(fill="x", padx=10, pady=14)
    ctk.CTkLabel(qa, text="⚡ Acciones rápidas", font=("Arial", 15, "bold")).pack(anchor="w", padx=14, pady=(10, 6))
    btns = ctk.CTkFrame(qa, fg_color="transparent")
    btns.pack(fill="x", padx=10, pady=(0, 12))
    for i in range(4):
        btns.grid_columnconfigure(i, weight=1)
    ctk.CTkButton(btns, text="🔧 Driver Center", command=lambda: ctx.goto("drivers")).grid(row=0, column=0, padx=6, sticky="ew")
    ctk.CTkButton(btns, text="📱 Mi dispositivo", command=lambda: ctx.goto("devices")).grid(row=0, column=1, padx=6, sticky="ew")
    ctk.CTkButton(btns, text="🧰 Biblioteca", command=lambda: ctx.goto("library")).grid(row=0, column=2, padx=6, sticky="ew")
    ctk.CTkButton(btns, text="💬 Telegram", command=lambda: ctx.open_link(config.TELEGRAM)).grid(row=0, column=3, padx=6, sticky="ew")

    feat = ctk.CTkFrame(root, corner_radius=12)
    feat.pack(fill="x", padx=10, pady=(0, 14))
    ctk.CTkLabel(feat, text="🔥 Video destacado", font=("Arial", 15, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
    ctk.CTkLabel(feat, text="🔓 NUSANTARA UNLOCK TOOL 2026 | Quita FRP, Mi Cloud y Bloqueo de Pantalla GRATIS",
                 font=("Arial", 13), wraplength=700, justify="left").pack(anchor="w", padx=14)
    ctk.CTkButton(feat, text="▶ Ver ahora en YouTube",
                  command=lambda: ctx.open_link("https://www.youtube.com/watch?v=UEZ_TTf-PLg")
                  ).pack(anchor="w", padx=14, pady=10)
    return root


def _install_pt(ctx, lbl):
    ctx.status("Descargando Platform-Tools oficiales de Google…")
    try:
        adb.ensure_platform_tools()
        lbl.configure(text="✅ Listo")
        ctx.status("Platform-Tools instalado. ✅")
    except Exception as e:
        ctx.status(f"Error: {e}")


def _detect(ctx, lbl):
    ctx.status("Buscando dispositivos…")
    try:
        if not adb.platform_tools_ready():
            adb.ensure_platform_tools()
        n = len(adb.list_adb_devices()) + len(adb.list_fastboot_devices())
        lbl.configure(text=f"📱 {n} detectado(s)" if n else "Sin dispositivos")
        ctx.status(f"Detección terminada: {n} dispositivo(s).")
    except Exception as e:
        lbl.configure(text="Error")
        ctx.status(f"Error: {e}")
