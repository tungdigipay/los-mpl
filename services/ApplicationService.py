from libraries import Kalapa, MFast, Hasura
from services import SmsSevice, ExecuteBgService, ScoringLogService
from helpers import CommonHelper

def credit_score(idNumber, mobilePhone):
    return Kalapa.process("user-profile/scoring/social_fraud", "GET", {
        "id": idNumber,
        "mobile": mobilePhone
    }, "credit_score")

def check_mobilephone(mobilePhone):
    return Kalapa.process("user-profile/mobile2id/get/", "GET", {
        "mobile": mobilePhone
    }, "check_mobilephone")

def social_insurance(idNumber):
    return Kalapa.process("user-profile/user-jscore/vc/get/", "GET", {
        "id": idNumber
    }, "social_insurance")

def mfast_blacklist(idNumber, mobilePhone):
    return MFast.process("/blacklist", "POST", {
        "idNumber": idNumber,
        "mobilePhone": mobilePhone
    })

def mfast_dedup(idNumber, mobilePhone):
    return MFast.process("/dedup", "POST", {
        "idNumber": idNumber,
        "mobilePhone": mobilePhone
    })

def dedup_in_los(applicationID, idNumber, mobilePhone):
    payload = {
        "idNumber": idNumber, 
        "mobilePhone": mobilePhone
    }
    acting = __check_dedup_in_los_active(idNumber, mobilePhone)
    result_content = {}
    
    result_content['Đã kích hoạt'] = "Chưa"
    if acting['status'] == False:
        result_content['Đã kích hoạt'] = acting['message']
        log_dedup_in_los(applicationID, payload, 'rejected', result_content)
        return acting

    result_content['Đang hoạt động'] = "Chưa"
    processing = __check_dedup_in_los_processing(idNumber, mobilePhone)
    if processing['status'] == False:
        result_content['Đang hoạt động'] = processing['message']
        log_dedup_in_los(applicationID, payload, 'rejected', result_content)
        return processing

    result_content['Từ chối < 30d'] = "Không"
    rejected = __check_dedup_in_los_rejected(idNumber, mobilePhone)
    if rejected['status'] == False:
        result_content['Từ chối < 30d'] = rejected['message']
        log_dedup_in_los(applicationID, payload, 'rejected', result_content)
        return rejected

    log_dedup_in_los(applicationID, payload, 'pass', result_content)

    return {
        "status": True,
        "message": "Thỏa điều kiện",
        "code": ""
    }

def __check_dedup_in_los_active(idNumber, mobilePhone):
    query = """
    query count_loan_by_phone {
        LOS_applications_aggregate(
            where: {
                LOS_customer_profile: {mobilePhone: {_eq: "%s"} }, 
                LOS_customer: {idNumber: {_eq: "%s"} }, 
                statusID: { _eq: 23 } 
            }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (mobilePhone, idNumber)
    res = Hasura.process("count_loan_by_phone", query)
    if res['status'] == False:
        return res
    
    number = res['data']['LOS_applications_aggregate']['aggregate']['count']
    if (number > 1):
        return {
            "status": False,
            "message": f"Có {number} khoản vay BNPL đang hoạt động",
            "code": "DDP_LCT1"
        }
    
    return {
        "status": True
    }

def __check_dedup_in_los_processing(idNumber, mobilePhone):
    processing_status_ids = CommonHelper.list_status_for_processing()
    status_ids = [str(element) for element in processing_status_ids]
    query = """
    query count_processing_by_phone {
        LOS_applications_aggregate(
            where: {
                LOS_customer_profile: {mobilePhone: {_eq: "%s"} }, 
                LOS_customer: {idNumber: {_eq: "%s"} }, 
                statusID: { _in: [%s] } 
            }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (mobilePhone, idNumber, ', '.join(status_ids))
    res = Hasura.process("count_processing_by_phone", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }
    
    number = res['data']['LOS_applications_aggregate']['aggregate']['count']
    if (number > 0):
        return {
            "status": False,
            "message": f"Có {number} khoản vay BNPL đang xử lý",
            "code": "DDP_LCT2"
        }
    
    return {
        "status": True
    }

def __check_dedup_in_los_rejected(idNumber, mobilePhone):
    rejected_status_ids = CommonHelper.list_status_for_rejected()
    status_ids = [str(element) for element in rejected_status_ids]
    thirty_days_ago = CommonHelper.thirty_days_ago()
    query = """
    query count_processing_by_phone {
        LOS_applications_aggregate(
            where: {
                LOS_customer_profile: {mobilePhone: {_eq: "%s"} }, 
                LOS_customer: {idNumber: {_eq: "%s"} }, 
                statusID: { _in: [%s] } 
                createdDate: { _gt: "%s"}
            }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (mobilePhone, idNumber, ', '.join(status_ids), thirty_days_ago)
    res = Hasura.process("count_processing_by_phone", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }
    
    number = res['data']['LOS_applications_aggregate']['aggregate']['count']
    if (number > 0):
        return {
            "status": False,
            "message": f"Có {number} khoản vay BNPL bị từ chối trong 30 ngày",
            "code": "DDP_LCT3"
        }
    
    return {
        "status": True
    }

def __check_dedup_in_los_refused(idNumber):
    query = """
    query q_LOS_applications_aggregate {
        LOS_applications_aggregate(
            where: { statusID : { _in: [5, 9, 11, 17] }, 
            LOS_customer: { idNumber: { _eq: "%s" } } }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (idNumber)
    res = Hasura.process("q_LOS_applications_aggregate", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }
    
    if (res['data']['LOS_applications_aggregate']['aggregate']['count'] > 0):
        return {
            "status": False,
            "message": "Có khoản vay BNPL bị từ chối dưới 30 ngày",
            "code": "DDP_LCT3"
        }
    
    return {
        "status": True
    }

def update_status(application, statusID, message):
    appID = application['ID']
    query = """
    mutation m_update_LOS_applications_by_pk {
        update_LOS_applications_by_pk(
            pk_columns: { ID: %d }, 
            _set: { 
                statusID: %d ,
                note: "%s"
            }
        ) {
            ID uniqueID
            LOS_customer_profile{
                mobilePhone
            }
        }
    }
    """ % (appID, statusID, message)

    res = Hasura.process("m_update_LOS_applications_by_pk", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }

    uniqueID = res['data']['update_LOS_applications_by_pk']['uniqueID']

    ## send sms when rejected (canceled/ confused)
    if statusID in CommonHelper.list_status_for_refused():
        mobilePhone = res['data']['update_LOS_applications_by_pk']['LOS_customer_profile']['mobilePhone']
        SmsSevice.reject(mobilePhone)

    ## callback status to mfast via webhook
    ExecuteBgService.postback(uniqueID=uniqueID)

    return {
        "status": True
    }

def log_dedup_in_los(applicationID, payload, result, result_content):
    ScoringLogService.record({
        "applicationID": applicationID, 
        "result": result, 
        "type": "dedup_in_house", 
        "label": "Dedup in house", 
        "logServiceID": 0
    }, payload, result_content)