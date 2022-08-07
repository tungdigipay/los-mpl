from pydantic import BaseModel, validator

class Item(BaseModel):
    mobilePhone: str

    @validator('mobilePhone')
    def mobilePhone_validator(cls, v, values, **kwargs):
        if v.isdigit() == False:
            raise ValueError("Not number")
        if len(v) != 10:
            raise ValueError("Length must be 10")
        if v[0] != '0':
            raise ValueError("Mobile Phone is invalid")
        return v

class Verify(BaseModel):
    otpCode: str
    UUID: str

    @validator('otpCode')
    def otpCode_valiadator(cls, v):
        if v.isdigit() == False:
            raise ValueError("Not number")
        if len(v) != 4:
            raise ValueError("Length must be 4")

        return v

    @validator('UUID')
    def UUID_validator(cls, v):
        from helpers.CommonHelper import is_uuid
        if is_uuid(v) == False:
            raise ValueError("UUID không hợp lệ")
        return v