from pydantic import BaseModel, validator
import re

class Item(BaseModel):
    mobilePhoneUUID: str
    fullName: str
    dateOfBirth: str
    genderID: int
    idNumber: str
    idNumber_dateOfIssue: str
    idNumber_issuePlace: str
    email: str
    marritalStatusID: int
    idNumberFrontImage: str
    idNumberBackImage: str
    status: str
    extractData: str

    @validator('idNumber_dateOfIssue')
    def idNumber_dateOfIssue_valiadator(cls, v):
        from helpers.CommonHelper import validate_date
        if validate_date(v) == True:
            return v
        raise ValueError("Ngày cấp CMND/ CCCD không hợp lệ")

    @validator('dateOfBirth')
    def dateOfBirth_valiadator(cls, v):
        from helpers.CommonHelper import validate_date
        if validate_date(v) == True:
            return v
        raise ValueError("Ngày sinh không hợp lệ")

    @validator('email')
    def email_valiadator(cls, v):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, v)):
            return v
        raise ValueError("Email không hợp lệ")

    @validator('idNumber')
    def idNumber_valiadator(cls, v):
        if(len(v) not in [9, 12]):
            raise ValueError("CMND/ CCCD không hợp lệ")
        return v