from pathlib import Path
from fastapi import File, UploadFile
from libraries import S3

async def upload(file):
    contents = await file.read()

    path = "./files/ocr"
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(f"{path}/{file.filename}", "wb") as f:
        f.write(contents)

    object_name = f"files/ocr/{file.filename}"
    return S3.upload(object_name, file.filename)