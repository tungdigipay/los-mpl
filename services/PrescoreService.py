from email.mime import application
from services import ApplicationService
from libraries import Hasura
from helpers import CommonHelper

def process(uniqueID):
    application = detail_by_appID(uniqueID)
    if application['status'] == False:
        return application

    application = application['data']
    if application['statusID'] != 3:
        return {
            "status": False,
            "message": "Hồ sơ chưa đạt yêu cầu Prescore"
        }

    applicationID = application['ID']
    birthday = application['LOS_customer']['dateOfBirth']
    loanTenor = application['loanTenor']
    monthly_income = application['monthlyIncome']
    districtID = application['LOS_customer_profile']['currentAddressProvince']

    res_age = __score_age(birthday, loanTenor)
    if res_age['status'] == False:
        ApplicationService.update_status(applicationID, 8, f"{res_age['code']}_{res_age['message']}")
        return res_age

    res_income = __score_income(monthly_income)
    if res_income['status'] == False:
        ApplicationService.update_status(applicationID, 8, f"{res_income['code']}_{res_income['message']}")
        return res_income

    res_region = __score_region(application)
    if res_region['status'] == False:
        ApplicationService.update_status(applicationID, 8, f"{res_region['code']}_{res_region['message']}")
        return res_region

    ApplicationService.update_status(applicationID, 7, "Kiểm tra eligible và đang chờ PHV")
    res_phv = __score_phv()
    if res_phv['status'] == False:
        ApplicationService.update_status(applicationID, 8, f"{res_phv['code']}_{res_phv['message']}")
        return res_phv

    ApplicationService.update_status(applicationID, 6, "Kiểm tra eligible/PHV/credit score")

    return {
        "status": True,
        "message": "Kiểm tra eligible/PHV/credit score"
    }


def __score_age(birthday, loanTenor):
    import math
    age = CommonHelper.get_age(birthday)
    age_months = age + math.ceil(loanTenor/ 12)
    if age_months > 60:
        return {
            "status": False,
            "message": "Ngoài độ tuổi hỗ trợ",
            "code": "ELI_AGER"
        }

    return {
        "status": True
    }
    
def __score_income(monthly_income):
    if monthly_income < 4500000:
        return {
            "status": False,
            "message": "Ngoài mức thu nhập hỗ trợ",
            "code": "ELI_INCR"
        }

    return {
        "status": True
    }

def __score_region(application):
    if application['LOS_master_location']['allow'] != 1:
        return {
            "status": False,
            "message": "Địa chỉ tạm trú/ chỗ ở hiện tại không nằm trong danh sách hỗ trợ ",
            "code": "ELI_COVR"
        }
    return {
        "status": True
    }

def __score_phv():
    return {
        "status": True
    }

def detail_by_appID(uniqueID):
    query = """
    query detail_LOS_applications {
        LOS_applications(
            where: { 
                uniqueID: { _eq: "%s" } 
            }
        ) {
            ID
            LOS_customer {
                dateOfBirth
            }
            monthlyIncome
            reference1Name
            reference1Phone
            reference1Relationship
            reference2Name
            reference2Phone
            reference2Relationship
            LOS_customer_profile {
                currentAddressProvince
            }
            LOS_master_location {
                allow
            }
            loanTenor
            statusID
        }
    }
    """ % (uniqueID)
    res = Hasura.process("detail_LOS_applications", query)
    if res['status'] == False:
        return res
    
    return {
        "status": True,
        "data": res['data']['LOS_applications'][0]
    }