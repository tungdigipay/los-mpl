from pydantic import BaseModel, validator
import re
import validators
from uuid import UUID

class Item(BaseModel):
    uniqueID: UUID
    faceImage: str
    extractData: str

    @validator('extractData')
    def extractData_valiadator(cls, v):
        from helpers.CommonHelper import is_json
        if is_json(v) == True:
            return v
        raise ValueError("Extract Data không hợp lệ")

    @validator('uniqueID')
    def uniqueID_validator(cls, v):
        from helpers.CommonHelper import is_uuid
        if is_uuid(v) == False:
            raise ValueError("uniqueID không hợp lệ")
        return v

    @validator('faceImage')
    def faceImage_validator(cls, v):
        valid = validators.url(v)
        if valid != True:
            raise ValueError("Hình selfie không hợp lệ")
        return v
        
