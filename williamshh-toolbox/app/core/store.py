"""Almacenamiento local (configuración, caché) + utilidades JSON."""
import json
import os


def get_app_dir():
    if os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        path = os.path.join(base, "WilliamsHHToolbox")
    else:
        path = os.path.join(os.path.expanduser("~"), ".williamshh-toolbox")
    os.makedirs(path, exist_ok=True)
    return path


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class Settings:
    def __init__(self):
        self.path = os.path.join(get_app_dir(), "settings.json")
        self.data = load_json(self.path, {"theme": "dark", "remote_updates": True})

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        save_json(self.path, self.data)

    def reset(self):
        self.data = {"theme": "dark", "remote_updates": True}
        save_json(self.path, self.data)
