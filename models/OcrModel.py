from cgitb import text
from datetime import date
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
    extractData: text

    @validator('email')
    def email_valiadator(cls, v):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, v)):
            return v
        else:
            raise ValueError("Invalid Email")