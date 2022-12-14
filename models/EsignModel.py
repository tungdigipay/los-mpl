from pydantic import BaseModel, validator, Field
from typing import Union
from uuid import UUID
from helpers import CommonHelper

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

class Email(BaseModel):
    uniqueID: UUID
    email: str

    @validator('email')
    def email_validator(cls, v):
        if CommonHelper.is_email(v) == False:
            raise ValueError("Email is invalid")
        return v