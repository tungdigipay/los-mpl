from libraries import Kalapa, MFast, Hasura
from services import SmsSevice, ExecuteBgService
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
    acting = __check_dedup_in_los_active(idNumber, mobilePhone)
    
    if acting['status'] == False:
        return acting

    processing = __check_dedup_in_los_processing(idNumber, mobilePhone)
    if processing['status'] == False:
        return processing

    rejected = __check_dedup_in_los_rejected(idNumber, mobilePhone)
    if rejected['status'] == False:
        return rejected

    return {
        "status": True,
        "message": "",
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
    
    if (res['data']['LOS_applications_aggregate']['aggregate']['count'] > 1):
        return {
            "status": False,
            "message": "Có hơn 1 khoản vay BNPL đang hoạt động",
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
    
    if (res['data']['LOS_applications_aggregate']['aggregate']['count'] > 0):
        return {
            "status": False,
            "message": "Có khoản vay BNPL đang xử lý",
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
    
    if (res['data']['LOS_applications_aggregate']['aggregate']['count'] > 0):
        return {
            "status": False,
            "message": "Có khoản vay BNPL bị từ chối dưới 30 ngày",
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
        SmsSevice.reject(application['LOS_customer_profile']['mobilePhone'])

    ## callback status to mfast via webhook
    ExecuteBgService.postback(uniqueID=uniqueID)

    return {
        "status": True
    }