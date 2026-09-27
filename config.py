"""Configuración global de WilliamsHH Toolbox PRO."""
import os
import sys

APP_NAME = "WilliamsHH Toolbox PRO"
VERSION = "1.0.0"
AUTHOR = "Williams HH"
TAGLINE = "La Caja de Herramientas del Técnico"

# ---- Links oficiales del canal (reales) ----
YOUTUBE_CHANNEL = "https://www.youtube.com/channel/UCmr8XUMRRTo6A5fKm_r07fA"
YOUTUBE_HANDLE = "https://www.youtube.com/@WilliamsHH-v3e"
TELEGRAM = "https://t.me/williamshhpro"
PLAYLIST_TOOLS = "https://youtube.com/playlist?list=PLbScE3ILRjxLqEXNFJYDVn1yLBmw2wywx"

# ---- Catálogo remoto: actualiza tools/drivers/tutoriales SIN recompilar ----
# Sube tu carpeta remote-catalog/ a GitHub y pega aquí tu URL raw.
# Ejemplo: "https://raw.githubusercontent.com/TU_USUARIO/toolbox-data/main/"
REMOTE_BASE = "https://raw.githubusercontent.com/williamshh/toolbox-data/main/"
REMOTE_VERSION_URL = REMOTE_BASE + "version.json"
REMOTE_TOOLS_URL = REMOTE_BASE + "tools.json"
REMOTE_DRIVERS_URL = REMOTE_BASE + "drivers.json"
REMOTE_TUTORIALS_URL = REMOTE_BASE + "tutorials.json"

# ---- Descargas directas oficiales (verificadas, funcionan) ----
PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
GOOGLE_USB_DRIVER_URL = "https://dl.google.com/android/repository/usb_driver_r13-windows.zip"
SAMSUNG_DRIVER_PAGE = "https://developer.samsung.com/mobile/android-usb-driver.html"


def resource_path(*parts):
    """Ruta a archivos internos (funciona en dev y en .exe compilado)."""
    if getattr(sys, "_MEIPASS", None):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, "app", *parts)
