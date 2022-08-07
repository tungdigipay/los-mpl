from pydantic import BaseModel, validator

class Item(BaseModel):
    file: str
    
    @validator ("file")
    def file_validation(cls, v):
        if v == "":
            raise ValueError("Lỗi dữ liệu")
        return v
