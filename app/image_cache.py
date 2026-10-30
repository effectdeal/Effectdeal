"""Small authenticated image previews. Cache files contain no credentials."""
import hashlib
import io
import os
import tempfile
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError


def thumbnail_path(tenant, record, loader):
    key=hashlib.sha256(f"{tenant}/{record['id']}/{record['version']}/640-v1".encode()).hexdigest()
    directory=Path(tempfile.gettempdir())/'effectdeal-previews'
    directory.mkdir(mode=0o700, exist_ok=True)
    target=directory/(key+'.webp')
    if target.exists():return target
    try:
        with Image.open(io.BytesIO(loader())) as source:
            image=ImageOps.exif_transpose(source)
            image.thumbnail((640,420))
            if image.mode not in ('RGB','RGBA'):image=image.convert('RGB')
            with tempfile.NamedTemporaryFile(dir=directory,delete=False) as tmp:
                temporary=Path(tmp.name)
            try:
                image.save(temporary,format='WEBP',quality=76)
                os.replace(temporary,target)
            finally:
                temporary.unlink(missing_ok=True)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return None
    return target
