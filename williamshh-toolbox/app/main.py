"""WilliamsHH Toolbox PRO - Ventana principal."""
import os
import sys
import webbrowser

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import customtkinter as ctk  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from PIL import Image  # noqa: E402

from app import config  # noqa: E402
from app.core.store import Settings  # noqa: E402
from app.modules import home, drivers, devices, library, tutorials, pcfix  # noqa: E402
from app.modules import settings as settings_mod  # noqa: E402

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{config.APP_NAME} v{config.VERSION}  •  {config.TAGLINE}")
        self.geometry("1140x730")
        self.minsize(1020, 660)
        ico = config.resource_path("assets", "icon.ico")
        if os.path.isfile(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        self.settings = Settings()
        ctk.set_appearance_mode(self.settings.get("theme", "dark"))

        self.ctx = SimpleNamespace(settings=self.settings, status=self.set_status,
                                   open_link=self.open_link, goto=self.goto)

        # ---- Sidebar ----
        side = ctk.CTkFrame(self, width=230, corner_radius=0)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        logo_p = config.resource_path("assets", "logo.png")
        if os.path.isfile(logo_p):
            try:
                img = Image.open(logo_p)
                img.thumbnail((210, 110))
                self._logo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                ctk.CTkLabel(side, image=self._logo, text="").pack(padx=10, pady=(14, 4))
            except Exception:
                pass
        ctk.CTkLabel(side, text=config.APP_NAME, font=("Arial", 15, "bold")).pack(padx=10)
        ctk.CTkLabel(side, text=f"v{config.VERSION}", font=("Arial", 11),
                     text_color="gray").pack(padx=10, pady=(0, 10))

        self.nav = {}
        pages = [("🏠  Inicio", "home"), ("🔧  Driver Center", "drivers"),
                 ("📱  Dispositivos", "devices"), ("🧰  Biblioteca", "library"),
                 ("📚  Tutoriales", "tutorials"), ("🩺  PC Fix", "pcfix"),
                 ("⚙  Ajustes", "settings")]
        for label, key in pages:
            b = ctk.CTkButton(side, text=label, anchor="w", height=38,
                              command=lambda k=key: self.goto(k))
            b.pack(fill="x", padx=12, pady=3)
            self.nav[key] = b

        side_bot = ctk.CTkFrame(side, fg_color="transparent")
        side_bot.pack(side="bottom", fill="x", padx=12, pady=12)
        ctk.CTkButton(side_bot, text="▶ YouTube", fg_color="#C0392B", height=32,
                      command=lambda: self.open_link(config.YOUTUBE_HANDLE)).pack(fill="x", pady=3)
        ctk.CTkButton(side_bot, text="💬 Telegram", height=32,
                      command=lambda: self.open_link(config.TELEGRAM)).pack(fill="x", pady=3)

        # ---- Contenido + estado ----
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(side="left", fill="both", expand=True)
        self.content = ctk.CTkFrame(main, fg_color="transparent")
        self.content.pack(fill="both", expand=True)
        self.status_lbl = ctk.CTkLabel(main, text="Listo. 💪", font=("Arial", 11),
                                       text_color="gray", anchor="w")
        self.status_lbl.pack(fill="x", padx=14, pady=(0, 8))

        self.builders = {"home": home.build_page, "drivers": drivers.build_page,
                         "devices": devices.build_page, "library": library.build_page,
                         "tutorials": tutorials.build_page, "pcfix": pcfix.build_page,
                         "settings": settings_mod.build_page}
        self.goto("home")

    def goto(self, key):
        for w in self.content.winfo_children():
            w.destroy()
        for k, b in self.nav.items():
            b.configure(fg_color="#1F6AA5" if k == key else "transparent",
                        text_color="white" if k == key else ("white", "white"))
        try:
            self.builders[key](self.content, self.ctx)
        except Exception as e:
            ctk.CTkLabel(self.content, text=f"❌ Error cargando: {e}").pack(pady=40)

    def set_status(self, msg):
        try:
            self.after(0, lambda: self.status_lbl.configure(text=str(msg)[:160]))
        except Exception:
            pass

    def open_link(self, url):
        webbrowser.open(url)


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
