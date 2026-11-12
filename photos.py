from fastapi import UploadFile
from pathlib import Path
import uuid
import shutil
from PIL import Image, ImageOps

Path('media').mkdir(exist_ok=True)

def save_photo(photo: UploadFile):
    # 파이썬 동작 코드
    # ext = Path(photo.filename).suffix # => image.jpeg
    # name = f'{uuid.uuid4().hex}{ext}' # 1523542524.jpeg

    # with open(f'media/{name}', 'wb') as f:
    #     shutil.copyfileobj(photo.file, f)

    # 필로우 기능 동작 코드
    image = Image.open(photo.file) # 방금 사용자가 업로드한 이미지
    # 필로우로 조작이 가능한 형태가 됨

    # 핸드폰 사진 회전 문제
    image = ImageOps.exif_transpose(image)
    # png 파일 변환
    image = image.convert('RGB')
    # 사진 사이즈 조절
    ImageOps.fit(image, (1080, 1080))

    name = f'{uuid.uuid4().hex}.jpg'
    image.save(f'media/{name}')



    return f'/media/{name}'