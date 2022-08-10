from uuid import UUID
from pydantic import BaseModel, validator, Field
from typing import Union

class Item(BaseModel):
    uniqueID: str
    productID: int = Field(gt=0, description="The price must be greater than zero")
    note: Union[str, None] = Field(
        default=None, title="Ghi chú hồ sơ", max_length=255
    )

    ## thông tin hiện tại
    currentAddressProvince: int
    currentAddressDistrict: int
    currentAddressWard: int
    currentAddressDetail: str

    # ## thông tin hộ khẩu
    permanentAddressProvince: int
    permanentAddressDistrict: int
    permanentAddressWard: int
    permanentAddressDetail: str

    employmentType: int ## loại nghề nghiệp
    companyName: str ## tên cty
    monthlyIncome: int ## thu nhập tháng
    monthlyExpenses: int ## chi phí hàng tháng

    bankID: int ## tên Ngân hàng
    bankAccountNumber: str ## số tài khoản ngân hàng
    bankAccountName: str ## tên chủ tài khoản

    ## thông tin tham chiếu 1
    reference1Name: str
    reference1Relationship: int 
    reference1Phone: Union[str, None] = Field(
        default=None, title="Số điện thoại người tham chiếu 1", max_length=10, min_length=10
    )

    ## thông tin tham chiếu 2
    reference2Name: str
    reference2Relationship: int 
    reference2Phone: Union[str, None] = Field(
        default=None, title="Số điện thoại người tham chiếu 2", max_length=10, min_length=10
    )

    ## thông tin khoản vay
    loanTenor: int = Field(gt=0, description="Thời hạn vay phải có")
    loanAmount: int = Field(gt=0, description="Khoản vay phải có")
    emi: int = Field(gt=0, description="Số tiền ước tính hàng tháng")

    @validator('uniqueID')
    def uniqueID_validator(cls, v):
        from helpers.CommonHelper import is_uuid
        if is_uuid(v) == False:
            raise ValueError("uniqueID không hợp lệ")
        return v

    @validator("reference2Phone")
    def referencePhone_validator(cls, v, values):
        if v == values['reference1Phone']:
            raise ValueError("Số điện thoại tham chiếu trùng nhau")
        return v

    @validator("reference2Relationship")
    def referenceRelationship_validator(cls, v, values):
        if v == values['reference1Relationship'] and v == 1:
            raise ValueError("Thông tin tham chiếu không hợp lệ")
        return v

    @validator("reference2Name")
    def referenceName_validator(cls, v, values):
        if v == values['reference1Name']:
            raise ValueError("Tên người tham chiếu trùng nhau")
        return v

class Prescore(BaseModel):
    uniqueID: UUID