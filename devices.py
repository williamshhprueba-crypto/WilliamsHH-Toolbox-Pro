"""Device Manager: controla tu Android con botones (ADB/Fastboot reales)."""
import threading

import customtkinter as ctk

from app.core import adb


def build_page(parent, ctx):
    root = ctk.CTkFrame(parent, fg_color="transparent")
    root.pack(fill="both", expand=True)
    state = {"devices": [], "menu": None, "info": None, "log": None}

    ctk.CTkLabel(root, text="📱 Device Manager", font=("Arial", 22, "bold")).pack(anchor="w", padx=14, pady=(10, 2))
    ctk.CTkLabel(root, text="Conecta tu equipo por USB con Depuración USB activada. Sin escribir comandos.",
                 font=("Arial", 12), text_color="gray").pack(anchor="w", padx=14, pady=(0, 8))

    bar = ctk.CTkFrame(root, fg_color="transparent")
    bar.pack(fill="x", padx=10)
    ctk.CTkButton(bar, text="🔍 Detectar dispositivos", width=200,
                  command=lambda: threading.Thread(target=lambda: _detect(ctx, state),
                                                   daemon=True).start()).pack(side="left", padx=4)
    state["menu"] = ctk.CTkOptionMenu(bar, values=["(pulsa Detectar)"], width=260)
    state["menu"].pack(side="left", padx=4)
    ctk.CTkButton(bar, text="📋 Leer información", width=170,
                  command=lambda: threading.Thread(target=lambda: _info(ctx, state),
                                                   daemon=True).start()).pack(side="left", padx=4)

    state["info"] = ctk.CTkTextbox(root, height=130, font=("Consolas", 12))
    state["info"].pack(fill="x", padx=14, pady=8)
    state["info"].insert("end", "Aquí verás marca, modelo, Android y compilación…\n")
    state["info"].configure(state="disabled")

    acts = ctk.CTkFrame(root, corner_radius=12)
    acts.pack(fill="x", padx=14, pady=4)
    ctk.CTkLabel(acts, text="⚡ Acciones de reinicio", font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(8, 4))
    grid = ctk.CTkFrame(acts, fg_color="transparent")
    grid.pack(fill="x", padx=8, pady=(0, 10))
    for i in range(4):
        grid.grid_columnconfigure(i, weight=1)
    buttons = [("🔄 Sistema", "system"), ("🛟 Recovery", "recovery"),
               ("⚙ Bootloader", "bootloader"), ("🟠 Fastboot", "fastboot"),
               ("⬛ EDL 9008", "edl"), ("💾 Download", "download"),
               ("📦 Sideload", "sideload"), ("🔁 Fastboot→Sistema", "fb_system")]
    for i, (label, mode) in enumerate(buttons):
        ctk.CTkButton(grid, text=label,
                      command=lambda m=mode: threading.Thread(
                          target=lambda: _reboot(ctx, state, m), daemon=True).start()
                      ).grid(row=i // 4, column=i % 4, padx=5, pady=4, sticky="ew")

    srv = ctk.CTkFrame(root, fg_color="transparent")
    srv.pack(fill="x", padx=10, pady=2)
    ctk.CTkButton(srv, text="▶ Iniciar servidor ADB", width=200,
                  command=lambda: threading.Thread(target=lambda: _srv(ctx, state, True),
                                                   daemon=True).start()).pack(side="left", padx=4)
    ctk.CTkButton(srv, text="⏹ Detener servidor ADB", width=200,
                  command=lambda: threading.Thread(target=lambda: _srv(ctx, state, False),
                                                   daemon=True).start()).pack(side="left", padx=4)

    state["log"] = ctk.CTkTextbox(root, height=110, font=("Consolas", 11))
    state["log"].pack(fill="both", expand=True, padx=14, pady=(6, 10))
    return root


def _log(state, msg):
    try:
        state["log"].insert("end", msg + "\n")
        state["log"].see("end")
    except Exception:
        pass


def _selected(state):
    v = state["menu"].get()
    if v.startswith("(pulsa"):
        return None, None
    serial, _, transport = v.partition("  |  ")
    return serial.strip(), transport.strip()


def _ensure(ctx, state):
    if not adb.platform_tools_ready():
        _log(state, "⬇ Descargando Platform-Tools oficiales (solo primera vez)…")
        adb.ensure_platform_tools()
        _log(state, "✅ Platform-Tools listo.")


def _detect(ctx, state):
    try:
        ctx.status("Detectando…")
        _ensure(ctx, state)
        devs = [f"{s}  |  adb ({st})" for s, st in adb.list_adb_devices()]
        devs += [f"{s}  |  fastboot" for s, st in adb.list_fastboot_devices()]
        state["devices"] = devs
        state["menu"].configure(values=devs or ["(sin dispositivos)"])
        if devs:
            state["menu"].set(devs[0])
        _log(state, f"🔍 {len(devs)} dispositivo(s): " + (", ".join(devs) if devs else "ninguno"))
        ctx.status("Detección terminada.")
    except Exception as e:
        _log(state, f"❌ {e}")
        ctx.status("Error detectando.")


def _info(ctx, state):
    try:
        serial, transport = _selected(state)
        if not serial:
            _log(state, "⚠️ Primero detecta y elige un dispositivo.")
            return
        if transport == "fastboot":
            _log(state, "⚠️ En modo fastboot no se puede leer info. Reinicia a sistema.")
            return
        ctx.status("Leyendo información…")
        info = adb.device_info(serial)
        box = state["info"]
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", f"Serie: {serial}\n")
        for k, v in info.items():
            box.insert("end", f"{k}: {v}\n")
        box.configure(state="disabled")
        _log(state, f"✅ Info de {serial}: {info.get('Marca')} {info.get('Modelo')} (Android {info.get('Android')})")
        ctx.status("Información lista.")
    except Exception as e:
        _log(state, f"❌ {e}")


def _reboot(ctx, state, mode):
    try:
        serial, transport = _selected(state)
        if mode == "fb_system":
            ok, out = adb.fastboot(["reboot"])
        elif transport == "fastboot":
            if mode in ("system",):
                ok, out = adb.fastboot(["reboot"])
            elif mode in ("bootloader", "fastboot"):
                ok, out = adb.fastboot(["reboot-bootloader"])
            else:
                _log(state, "⚠️ En fastboot solo: Sistema / Bootloader.")
                return
        else:
            ok, out = adb.reboot(mode, serial)
        _log(state, (f"✅ {mode}: {out}" if ok else f"❌ {mode}: {out}") or f"✅ {mode} enviado.")
        ctx.status("Comando enviado.")
    except Exception as e:
        _log(state, f"❌ {e}")


def _srv(ctx, state, start):
    ok, out = adb.start_server() if start else adb.kill_server()
    _log(state, f"✅ Servidor {'iniciado' if start else 'detenido'}. {out}")
