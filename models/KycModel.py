from pydantic import BaseModel, validator
import re

class Item(BaseModel):
    uniqueID: str
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
        
