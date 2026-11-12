from fastapi import UploadFile
from pathlib import Path
import uuid
import shutil

Path('media').mkdir(exist_ok=True)

def save_photo(photo: UploadFile):
    ext = Path(photo.filename).suffix # => image.jpeg
    name = f'{uuid.uuid4().hex}{ext}' # 1523542524.jpeg

    with open(f'media/{name}', 'wb') as f:
        shutil.copyfileobj(photo.file, f)

    return f'/media/{name}'