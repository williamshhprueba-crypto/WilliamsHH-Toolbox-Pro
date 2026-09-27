"""Tutorial Hub: videos del canal con miniatura, por categorías."""
import os
import threading
import webbrowser

import customtkinter as ctk
from PIL import Image

from app.core import remote
from app.core.store import get_app_dir


def build_page(parent, ctx):
    root = ctk.CTkFrame(parent, fg_color="transparent")
    root.pack(fill="both", expand=True)
    state = {"videos": [], "grid": None, "cat": None, "imgs": []}

    ctk.CTkLabel(root, text="📚 Tutoriales del Canal", font=("Arial", 22, "bold")).pack(anchor="w", padx=14, pady=(10, 2))

    bar = ctk.CTkFrame(root, fg_color="transparent")
    bar.pack(fill="x", padx=10, pady=4)
    state["cat"] = ctk.CTkOptionMenu(bar, values=["Todos"], width=200, command=lambda _v: _render(ctx, state))
    state["cat"].pack(side="left", padx=4)
    ctk.CTkButton(bar, text="🔄 Actualizar", width=130,
                  command=lambda: threading.Thread(target=lambda: _load(ctx, state),
                                                   daemon=True).start()).pack(side="left", padx=4)

    state["grid"] = ctk.CTkScrollableFrame(root, fg_color="transparent")
    state["grid"].pack(fill="both", expand=True, padx=6, pady=(0, 10))

    threading.Thread(target=lambda: _load(ctx, state), daemon=True).start()
    return root


def _load(ctx, state):
    ctx.status("Cargando tutoriales…")
    vids = remote.get_catalog("tutorials", use_remote=ctx.settings.get("remote_updates", True))
    state["videos"] = vids if isinstance(vids, list) else []
    cats = ["Todos"] + sorted({v.get("cat", "Otros") for v in state["videos"]})
    try:
        state["cat"].configure(values=cats)
        _render(ctx, state)
        ctx.status(f"{len(state['videos'])} tutoriales. ✅")
    except Exception:
        pass


def _render(ctx, state):
    try:
        cat = state["cat"].get()
        for w in state["grid"].winfo_children():
            w.destroy()
        state["imgs"] = []
        col = 0
        for v in state["videos"]:
            if cat != "Todos" and v.get("cat") != cat:
                continue
            _vcard(ctx, state, v, col)
            col += 1
    except Exception:
        pass


def _vcard(ctx, state, v, i):
    f = ctk.CTkFrame(state["grid"], corner_radius=12, width=250)
    f.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="n")
    img_lbl = ctk.CTkLabel(f, text="⌛", width=232, height=130, fg_color="#222", corner_radius=8)
    img_lbl.pack(padx=8, pady=(8, 4))
    ctk.CTkLabel(f, text=v.get("title", "")[:90], font=("Arial", 11),
                 wraplength=230, justify="left").pack(padx=8, pady=2)
    ctk.CTkButton(f, text="▶ Ver en YouTube", height=30,
                  command=lambda: webbrowser.open(f"https://www.youtube.com/watch?v={v['id']}")
                  ).pack(padx=8, pady=(2, 8))
    threading.Thread(target=lambda: _thumb(state, img_lbl, v["id"]), daemon=True).start()


def _thumb(state, label, vid):
    try:
        import requests
        cache = os.path.join(get_app_dir(), "cache", "thumbs", vid + ".jpg")
        if not os.path.isfile(cache):
            r = requests.get(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", timeout=10,
                             headers={"User-Agent": "WilliamsHH-Toolbox-PRO"})
            r.raise_for_status()
            os.makedirs(os.path.dirname(cache), exist_ok=True)
            with open(cache, "wb") as fh:
                fh.write(r.content)
        img = ctk.CTkImage(light_image=Image.open(cache), dark_image=Image.open(cache), size=(232, 130))
        state["imgs"].append(img)
        label.configure(image=img, text="")
    except Exception:
        try:
            label.configure(text="▶")
        except Exception:
            pass
