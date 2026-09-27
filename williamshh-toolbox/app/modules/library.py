"""Tool Library: biblioteca curada de herramientas + descargas directas."""
import os
import threading
import webbrowser

import customtkinter as ctk

from app.core import downloader, remote


def build_page(parent, ctx):
    root = ctk.CTkFrame(parent, fg_color="transparent")
    root.pack(fill="both", expand=True)
    state = {"tools": [], "list": None, "search": None, "cat": None, "progress": None}

    ctk.CTkLabel(root, text="🧰 Biblioteca de Herramientas", font=("Arial", 22, "bold")).pack(anchor="w", padx=14, pady=(10, 2))

    bar = ctk.CTkFrame(root, fg_color="transparent")
    bar.pack(fill="x", padx=10, pady=4)
    state["search"] = ctk.CTkEntry(bar, placeholder_text="🔍 Buscar herramienta…", width=280)
    state["search"].pack(side="left", padx=4)
    state["search"].bind("<KeyRelease>", lambda _e: _render(ctx, state))
    state["cat"] = ctk.CTkOptionMenu(bar, values=["Todas"], width=180, command=lambda _v: _render(ctx, state))
    state["cat"].pack(side="left", padx=4)
    ctk.CTkButton(bar, text="🔄 Actualizar", width=130,
                  command=lambda: threading.Thread(target=lambda: _load(ctx, state),
                                                   daemon=True).start()).pack(side="left", padx=4)

    state["progress"] = ctk.CTkProgressBar(root, height=12)
    state["progress"].pack(fill="x", padx=14, pady=4)
    state["progress"].set(0)

    state["list"] = ctk.CTkScrollableFrame(root, fg_color="transparent")
    state["list"].pack(fill="both", expand=True, padx=6, pady=(0, 10))

    threading.Thread(target=lambda: _load(ctx, state), daemon=True).start()
    return root


def _load(ctx, state):
    ctx.status("Cargando biblioteca…")
    tools = remote.get_catalog("tools", use_remote=ctx.settings.get("remote_updates", True))
    state["tools"] = tools if isinstance(tools, list) else []
    cats = ["Todas"] + sorted({t.get("category", "Otras") for t in state["tools"]})
    try:
        state["cat"].configure(values=cats)
        _render(ctx, state)
        ctx.status(f"{len(state['tools'])} herramientas cargadas. ✅")
    except Exception:
        pass


def _render(ctx, state):
    try:
        q = (state["search"].get() or "").lower()
        cat = state["cat"].get()
        for w in state["list"].winfo_children():
            w.destroy()
        for t in state["tools"]:
            if cat != "Todas" and t.get("category") != cat:
                continue
            if q and q not in (t.get("name", "") + t.get("desc", "")).lower():
                continue
            _card(ctx, state, t)
    except Exception:
        pass


def _card(ctx, state, t):
    f = ctk.CTkFrame(state["list"], corner_radius=12)
    f.pack(fill="x", padx=8, pady=5)
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=12, pady=(8, 0))
    ctk.CTkLabel(top, text=t.get("name", "?"), font=("Arial", 14, "bold")).pack(side="left")
    badge = t.get("badge") or t.get("category", "")
    ctk.CTkLabel(top, text=f"  {badge}  ", font=("Arial", 11, "bold"),
                 fg_color="#1F6AA5", corner_radius=8).pack(side="right")
    ctk.CTkLabel(f, text=t.get("desc", ""), font=("Arial", 12), text_color="gray",
                 wraplength=700, justify="left").pack(anchor="w", padx=12)
    btns = ctk.CTkFrame(f, fg_color="transparent")
    btns.pack(fill="x", padx=12, pady=8)
    if t.get("download_url"):
        ctk.CTkButton(btns, text="⬇ Descargar", width=140,
                      command=lambda tt=t: threading.Thread(
                          target=lambda: _download(ctx, state, tt), daemon=True).start()
                      ).pack(side="left", padx=(0, 8))
    else:
        ctk.CTkLabel(btns, text="🔗 Link en el video tutorial", font=("Arial", 11),
                     text_color="#F5B041").pack(side="left", padx=(0, 8))
    if t.get("page_url"):
        ctk.CTkButton(btns, text="🌐 Página", width=110, fg_color="#3B3B3B",
                      command=lambda u=t["page_url"]: webbrowser.open(u)).pack(side="left", padx=(0, 8))
    if t.get("tutorial_url"):
        ctk.CTkButton(btns, text="▶ Tutorial", width=110, fg_color="#C0392B",
                      command=lambda u=t["tutorial_url"]: webbrowser.open(u)).pack(side="left")


def _download(ctx, state, t):
    try:
        ctx.status(f"Descargando {t['name']}…")
        folder = os.path.join(os.path.expanduser("~"), "Downloads", "WilliamsHH")
        fname = t.get("filename") or t["download_url"].split("/")[-1].split("?")[0] or (t["id"] + ".zip")
        dest = os.path.join(folder, fname)
        downloader.download(t["download_url"], dest,
                            progress=lambda a, b: state["progress"].set(a / b if b else 0))
        state["progress"].set(1)
        ctx.status(f"✅ Guardado en: {dest}")
    except Exception as e:
        ctx.status(f"❌ Error descargando: {e}")
