from pathlib import Path
from fastapi import File, UploadFile
from libraries import S3
import base64, os
from datetime import datetime
import random, string

async def upload(file):
    today = datetime.now()
    name = today.strftime("%Y%m%d%H%M%S") + (''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))) + ".jpg"
    path = "./files/ocr"
    Path(path).mkdir(parents=True, exist_ok=True)
    object_name = f"{path}/{name}"
    with open(object_name, "wb") as fh:
        fh.write(base64.urlsafe_b64decode(file))

    file_uploaded = S3.upload(object_name, name)
    os.remove(object_name) 

    return file_uploaded