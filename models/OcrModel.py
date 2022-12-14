from pydantic import BaseModel, validator, Field
import re
from typing import Union
import validators
from uuid import UUID

class Item(BaseModel):
    type: str
    uniqueID: Union[str, None] = Field(
        default=None, title="Mã hồ sơ"
    )
    mobilePhoneUUID: UUID
    fullName: str
    dateOfBirth: str
    genderID: int
    idNumber: str
    idNumber_dateOfIssue: str
    idNumber_issuePlace: str
    email: str = None
    marritalStatusID: int = None
    idNumberFrontImage: str
    idNumberBackImage: str
    status: str
    extractData: str

    @validator("type")
    def type_validator(cls, v):
        if v not in ["init", "update"]:
            raise ValueError("Type must be init or update")
        return v

    @validator('idNumber_dateOfIssue')
    def idNumber_dateOfIssue_valiadator(cls, v):
        from helpers.CommonHelper import validate_date
        if validate_date(v) == True:
            return v
        raise ValueError("Ngày cấp CMND/ CCCD không hợp lệ")

    @validator('dateOfBirth')
    def dateOfBirth_valiadator(cls, v):
        from helpers.CommonHelper import validate_date, get_age
        if validate_date(v) != True:
            raise ValueError("Ngày sinh không hợp lệ")

        if get_age(v) < 20:
            raise ValueError("Rất tiếc bạn chưa đủ tuổi để tham gia chương trình")
        return v

    @validator('email')
    def email_valiadator(cls, v, values, **kwargs):
        if values['type']:
            return v
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, v)):
            return v
        raise ValueError("Email không hợp lệ")

    @validator('idNumber')
    def idNumber_valiadator(cls, v):
        if(len(v) not in [9, 12]):
            raise ValueError("CMND/ CCCD không hợp lệ")
        return v

    @validator('extractData')
    def extractData_validator(cls, v):
        from helpers.CommonHelper import is_json
        if is_json(v) == True:
            return v
        raise ValueError("extractData không hợp lệ")

    @validator('idNumberFrontImage')
    def idNumberFrontImage_validator(cls, v):
        valid = validators.url(v)
        if valid != True:
            raise ValueError("Mặt trước CMND/ CCCD không hợp lệ")
        return v

    @validator('idNumberBackImage')
    def idNumberBackImage_validator(cls, v):
        valid = validators.url(v)
        if valid != True:
            raise ValueError("extractData không hợp lệ")
        return v