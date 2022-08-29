from libraries import Kalapa, MFast, Hasura
from services import SmsService, ExecuteBgService, ScoringLogService
from helpers import CommonHelper
from apps import Postback

def credit_score(applicationID, idNumber, mobilePhone):
    payload = {
        "id": idNumber,
        "mobile": mobilePhone
    }
    type = "credit_score"
    resultContent = []
    result = ""

    res = Kalapa.process("user-profile/scoring/social_fraud", "GET", payload, type)
    if res ['status'] == True:
        result = "pass"
        resultContent.append({
            "score": res['data']['score'],
            "version": res['data']['version'],
        })
    else:
        result = "rejected"
        resultContent.append({
            "message": res['message']
        })

    ScoringLogService.record({
        "applicationID": applicationID,
        "type": type,
        "payload": payload,
        "resultContent": resultContent,
        "responseData": res,
        "logServiceID": res['logID'],
        "label": "Credit Score",
        "result": result
    })

    return res

def check_mobilephone(applicationID, mobilePhone):
    payload = {
        "mobile": mobilePhone
    }
    type = "check_mobilephone"
    resultContent = []
    result = ""

    res = Kalapa.process("user-profile/mobile2id/get/", "GET", payload, type)
    if res ['status'] == True:
        result = "pass"
        if res['data'] != None:
            for item in res['data']['ids']:
                resultContent.append({
                    "CMND/ CCCD": item['id'],
                    "Ngày sinh": item['dob'],
                    "Họ tên": item['name'],
                    "Địa chỉ": item['address'],
                })
        else:
            result = "rejected"
            resultContent.append({
                "message": "No result"
            })
    else:
        result = "rejected"
        resultContent.append({
            "message": res['message']
        })

    ScoringLogService.record({
        "applicationID": applicationID,
        "type": type,
        "payload": payload,
        "resultContent": resultContent,
        "responseData": res,
        "logServiceID": res['logID'],
        "label": "Telco",
        "result": result
    })

    return res

def social_insurance(applicationID, idNumber):
    payload = {
        "id": idNumber
    }
    resultContent = []
    res = Kalapa.process("user-profile/user-jscore/vc/get/", "GET", payload, "social_insurance")

    if res['status'] == True :
        result = "pass"
        for item in res['data']['sInfos']:
            resultContent.append({
                "Tên Công ty": item['companyName'],
                "Mã Công ty": item['companyCode'],
                "Thời gian": f"{item['startDate']} đến {item['endDate']}",
                "Điểm": item['score'],
            })
    else:
        result = "failed"
        resultContent.append({
            "message": res['message']
        })

    ScoringLogService.record({
        "applicationID": applicationID,
        "type": "social_insurance",
        "payload": payload,
        "resultContent": resultContent,
        "responseData": res,
        "logServiceID": res['logID'],
        "label": "Social Insurance",
        "result": result
    })

    return res

def mfast_blacklist(applicationID, idNumber, mobilePhone):
    payload = {
        "id": idNumber,
        "mobile": mobilePhone
    }
    type = "dgp_blacklist"
    resultContent = []
    result = ""

    res = MFast.process("/blacklist", "POST", payload)

    resultContent.append({
        "message": res['message']
    })
    if res['status'] == True: 
        result = "pass" 
    else: 
        result = "rejected"

    ScoringLogService.record({
        "applicationID": applicationID, 
        "result": result, 
        "type": type, 
        "label": "DGP Blacklist", 
        "logServiceID": 0,
        "payload": payload,
        "resultContent": resultContent,
        "responseData": res
    })

    return res

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
    result_content = []
    
    result_content.append({
        "Đã kích hoạt": "Chưa" if acting['status'] == True else acting['message']
    })
    if acting['status'] == False:
        log_dedup_in_los(applicationID, payload, 'rejected', result_content)
        return acting
        
    processing = __check_dedup_in_los_processing(idNumber, mobilePhone)
    result_content.append({
        "Đang hoạt động": "Chưa" if processing['status'] == True else processing['message']
    })
    if processing['status'] == False:
        log_dedup_in_los(applicationID, payload, 'rejected', result_content)
        return processing
        
    rejected = __check_dedup_in_los_rejected(idNumber, mobilePhone)
    result_content.append({
        "Từ chối < 30d": "Chưa" if rejected['status'] == True else rejected['message']
    })
    if rejected['status'] == False:
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

    ## send sms when rejected (canceled/ rejected)
    if statusID in CommonHelper.list_status_for_refused():
        mobilePhone = res['data']['update_LOS_applications_by_pk']['LOS_customer_profile']['mobilePhone']
        if statusID in CommonHelper.list_status_for_rejected():
            SmsService.reject(mobilePhone)
        else:
            SmsService.cancel(mobilePhone)

    ## callback status to mfast via webhook
    ## ExecuteBgService.postback(uniqueID=uniqueID)
    Postback.status(uniqueID)

    return {
        "status": True
    }

def log_dedup_in_los(applicationID, payload, result, result_content):
    ScoringLogService.record({
        "applicationID": applicationID, 
        "result": result, 
        "type": "dedup_in_house", 
        "label": "Dedup in house", 
        "logServiceID": 0,
        "payload": payload,
        "resultContent": result_content,
        "responseData": []
    })