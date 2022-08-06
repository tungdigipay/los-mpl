from pydantic import BaseModel, validator

class Item(BaseModel):
    file: str
