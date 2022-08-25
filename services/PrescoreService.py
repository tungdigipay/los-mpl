from services import ApplicationService, ExecuteBgService
from helpers import CommonHelper
from repositories import PrescoreRepository

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
        ApplicationService.update_status(application, 8, f"{res_age['code']}_{res_age['message']}")
        return res_age

    res_income = __score_income(monthly_income)
    if res_income['status'] == False:
        ApplicationService.update_status(application, 8, f"{res_income['code']}_{res_income['message']}")
        return res_income

    if application['reference1Relationship'] == 1 or ['reference2Relationship'] == 1:
        relationPhone = application['reference1Phone'] if application['reference1Relationship'] == 1 else application['reference2Phone']
        res_relation = __score_relation(relationPhone)
        if res_relation['status'] == False:
            ApplicationService.update_status(application, 8, f"{res_relation['code']}_{res_relation['message']}")
        return res_relation

    res_region = __score_region(application)
    if res_region['status'] == False:
        ApplicationService.update_status(application, 8, f"{res_region['code']}_{res_region['message']}")
        return res_region

    ApplicationService.update_status(application, 7, "Kiểm tra eligible và đang chờ PHV")
    res_phv = __score_phv()
    if res_phv['status'] == False:
        ApplicationService.update_status(application, 8, f"{res_phv['code']}_{res_phv['message']}")
        return res_phv

    ApplicationService.update_status(application, 6, "Kiểm tra eligible/PHV/credit score")
    ExecuteBgService.score(uniqueID)
    
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

def __score_relation(relationPhone):
    count_loan = PrescoreRepository.count_loan_by_phone(mobilePhone=relationPhone)
    if count_loan > 0:
        return {
            "status": False,
            "message": "Vợ/chồng đang có khoản vay BNPL",
            "code": "ELI_REF1"
        }

    count_processing = PrescoreRepository.count_processing_by_phone(mobilePhone=relationPhone)
    if count_processing > 0:
        return {
            "status": False,
            "message": "Vợ/chồng có hồ sơ BNPL đang xử lý",
            "code": "ELI_REF1"
        }

    count_refused = PrescoreRepository.count_refused_by_phone(mobilePhone=relationPhone)
    if count_processing > 0:
        return {
            "status": False,
            "message": "Vợ/chồng có hồ sơ BNPL bị từ chối dưới 30 ngày",
            "code": "ELI_REF3"
        }

    return {
        "status": True
    }

def __score_region(application):
    if application['LOS_customer_profile']['current_LOS_master_location_district']['allow'] != 1:
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
    return PrescoreRepository.detail_by_appID(uniqueID=uniqueID)