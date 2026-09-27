"""Catálogo remoto: actualiza contenido sin recompilar (con caché local)."""
import os

import requests

from app import config
from app.core.store import get_app_dir, load_json, save_json

CATALOGS = {
    "tools": (config.REMOTE_TOOLS_URL, "tools.json"),
    "drivers": (config.REMOTE_DRIVERS_URL, "drivers.json"),
    "tutorials": (config.REMOTE_TUTORIALS_URL, "tutorials.json"),
}


def fetch_json(url, timeout=12):
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "WilliamsHH-Toolbox-PRO"})
    r.raise_for_status()
    return r.json()


def get_catalog(name, use_remote=True):
    url, fname = CATALOGS[name]
    local = load_json(config.resource_path("data", fname), [])
    if not use_remote:
        return local
    try:
        data = fetch_json(url)
        save_json(os.path.join(get_app_dir(), "cache", fname), data)
        return data
    except Exception:
        cached = load_json(os.path.join(get_app_dir(), "cache", fname), None)
        return cached if cached is not None else local


def check_update(current_version, use_remote=True):
    """Devuelve dict {version, notes, url} si hay versión nueva, o None."""
    if not use_remote:
        return None
    try:
        info = fetch_json(config.REMOTE_VERSION_URL)
        if info.get("version") and str(info["version"]).strip() != str(current_version).strip():
            return info
    except Exception:
        pass
    return None
