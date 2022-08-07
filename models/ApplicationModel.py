from pydantic import BaseModel, validator

class Item(BaseModel):
    productID: int
    note: str

    @validator("productID")
    def productID_validator(cls, v):
        if v < 1:
            raise ("Product must be has value")
        return v