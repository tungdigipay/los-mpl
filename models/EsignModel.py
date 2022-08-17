from pydantic import BaseModel, validator, Field
from typing import Union
from uuid import UUID

class Preparing(BaseModel):
    agreementUUID: str

class Authorize(BaseModel):
    agreementUUID: str
    otpCode: str
    billCode: str

class Verify(BaseModel):
    contractNumber: str
    idNumber: str
    password: str

    @validator('idNumber')
    def idNumber_valiadator(cls, v):
        if(len(v) not in [9, 12]):
            raise ValueError("CMND/ CCCD không hợp lệ")
        return v

class Otp(BaseModel):
    uniqueID: UUID

class Confirm(BaseModel):
    uniqueID: UUID
    otpCode: str

    @validator('otpCode')
    def otpCode_valiadator(cls, v):
        if v.isdigit() == False:
            raise ValueError("Not number")
        if len(v) != 6:
            raise ValueError("Length must be 6")

        return v

    @validator('UUID')
    def UUID_validator(cls, v):
        from helpers.CommonHelper import is_uuid
        if is_uuid(v) == False:
            raise ValueError("UUID không hợp lệ")
        return v