"""Descargas con progreso + descompresión + hash."""
import hashlib
import os
import zipfile

import requests

CHUNK = 1024 * 512
HEADERS = {"User-Agent": "WilliamsHH-Toolbox-PRO"}


def download(url, dest, progress=None, timeout=60):
    """Descarga un archivo mostrando progreso. progress(done_bytes, total_bytes)."""
    folder = os.path.dirname(dest)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout, headers=HEADERS) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        done = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(CHUNK):
                if not chunk:
                    continue
                f.write(chunk)
                done += len(chunk)
                if progress:
                    progress(done, total)
    return dest


def extract_zip(zip_path, dest_dir, progress=None):
    with zipfile.ZipFile(zip_path) as z:
        members = z.namelist()
        total = len(members) or 1
        for i, m in enumerate(members, 1):
            z.extract(m, dest_dir)
            if progress:
                progress(i, total)
    return dest_dir


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(65536), b""):
            h.update(c)
    return h.hexdigest()


def fmt_size(num):
    if not num:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"
