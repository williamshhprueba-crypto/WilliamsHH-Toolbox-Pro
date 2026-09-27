[README.md](https://github.com/user-attachments/files/32697480/README.md)

# 🧰 WilliamsHH Toolbox PRO

**La Caja de Herramientas del Técnico** — todo lo que necesitas para servicio de celulares y PC, en un solo programa, en español y gratis.

![logo](app/assets/logo.png)

Hecha con 💪 por **Williams HH** — [YouTube](https://www.youtube.com/@WilliamsHH-v3e) • [Telegram](https://t.me/williamshhpro) • [Playlist Herramientas](https://youtube.com/playlist?list=PLbScE3ILRjxLqEXNFJYDVn1yLBmw2wywx)

---

## ✨ Qué incluye (6 módulos)

| Módulo | Qué hace |
|---|---|
| 🏠 **Inicio** | Panel con estado de ADB, accesos rápidos y video destacado |
| 🔧 **Driver Center** | Instala drivers MTK, Qualcomm 9008, Samsung y ADB con 1 clic. Detecta cuáles te faltan con `pnputil` real |
| 📱 **Device Manager** | Detecta tu Android, lee marca/modelo/Android y reinicia a Sistema, Recovery, Bootloader, Fastboot, **EDL 9008**, Download y Sideload. Sin escribir comandos |
| 🧰 **Biblioteca** | Herramientas curadas con descarga directa, página oficial y botón al video tutorial |
| 📚 **Tutoriales** | Los videos del canal con miniatura, por categorías (Unlock, FRP, Flasheo, Hard Reset, PC…) |
| 🩺 **PC Fix** | Mata ADB colgado, reinicia servidor, ve puertos COM, abre Administrador de dispositivos, guía de drivers sin firma |
| ⚙ **Ajustes** | Tema oscuro/claro, actualizaciones automáticas, acerca de |

ADB y Fastboot son **reales**: la app descarga sola las Platform-Tools oficiales de Google la primera vez (~8 MB).

---

## 🚀 Cómo conseguir el .exe (elige 1 opción)

### Opción A — Automático en la nube (recomendada, sin instalar nada)
1. Crea un repositorio en GitHub y sube esta carpeta.
2. En GitHub ve a **Releases → Create release → tag `v1.0.0`** y publícala.
3. Espera 3-5 minutos: el archivo **`WilliamsHH-Toolbox-PRO.exe`** aparece solo en el Release. ¡Descárgalo y listo!

### Opción B — En tu PC
1. Instala [Python 3.10+](https://www.python.org/downloads/) (marca ✅ **Add to PATH**).
2. Doble clic a **`build_exe.bat`** y espera.
3. Tu programa sale en la carpeta **`dist\WilliamsHH-Toolbox-PRO.exe`**.

### Opción C — Probar sin compilar
```
pip install -r requirements.txt
python app/main.py
```

> 💡 Consejo: ejecuta el `.exe` como **Administrador** para instalar drivers sin problemas.

---

## 🔄 Actualizar herramientas y videos SIN recompilar

La app lee su catálogo de internet si lo configuras (si no hay internet, usa el que trae dentro):

1. Crea un repo `toolbox-data` en GitHub con los archivos `version.json`, `tools.json`, `drivers.json`, `tutorials.json` (usa los de `app/data/` como base).
2. En `app/config.py` cambia `REMOTE_BASE` por tu URL raw:
   `https://raw.githubusercontent.com/TU_USUARIO/toolbox-data/main/`
3. Desde ese momento, agregar una herramienta o video = editar el JSON en GitHub. La app lo toma sola. 🚀

Hay una plantilla en `remote-catalog/version.json`.

---

## 📁 Estructura

```
williamshh-toolbox/
├── app/
│   ├── main.py          ← ventana principal
│   ├── config.py        ← versión, links, catálogo remoto
│   ├── core/            ← adb.py, downloader.py, remote.py, store.py, system_info.py
│   ├── modules/         ← home, drivers, devices, library, tutorials, pcfix, settings
│   ├── data/            ← drivers.json, tools.json, tutorials.json, links.json
│   └── assets/          ← logo.png, icon.png, icon.ico
├── .github/workflows/   ← compilación automática del .exe
├── build_exe.bat        ← compilar en tu PC con doble clic
├── requirements.txt
└── tests/smoke_test.py  ← python tests/smoke_test.py
```

---

## 🗺️ Hoja de ruta (próximas versiones)

- **v1.1** — Lector de firmware recomendado por modelo + respaldo de drivers instalados
- **v1.2** — Modo portable 100% + instalador con acceso directo
- **v2.0** — Login opcional de suscriptores + herramientas exclusivas + notificaciones de videos nuevos

---

## ⚠️ Aviso

Herramienta educativa para técnicos. Úsala solo en **equipos de tu propiedad** y respeta las leyes de tu país. Los drivers y programas pertenecen a sus respectivos autores (Google, Samsung, MediaTek, Qualcomm…).

© 2026 Williams HH. Todos los derechos reservados del diseño y marca.
