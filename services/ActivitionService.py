from services import ActivitionService, ApplicationService, ExecuteBgService, SmsSevice
from datetime import datetime
from libraries import Hasura

def process(uniqueID):
    application = ActivitionService.detail_application(uniqueID=uniqueID)
    if application == []:
        return {
            "status": False,
            "message": "Không tìm thấy hồ sơ"
        }

    if application['statusID'] != 22:
        return {
            "status": False,
            "message": "Hồ sơ chưa đủ điều kiện xử lý"
        }

    applicationID = application['ID']
    res = ApplicationService.update_activition(applicationID)
    application = res['data']
    ## active insurance after activition loan here
    __send_sms(application)

    return {
        "status": True,
        "message": "Thành công"
    }

def update_activition(applicationID):
    statusID = 23
    disbursedDate = datetime.now()
    query = """
    mutation m_update_LOS_applications_by_pk {
        update_LOS_applications_by_pk(
            pk_columns: { ID: %d }, 
            _set: { 
                statusID: %d ,
                note: "",
                disbursedDate: "%s"
            }
        ) {
            ID uniqueID contractNumber
            LOS_customer_profile{
                mobilePhone
            }
            LOS_customer{
                fullName
            }
        }
    }
    """ % (applicationID, statusID, disbursedDate)

    res = Hasura.process("m_update_LOS_applications_by_pk", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }

    uniqueID = res['data']['update_LOS_applications_by_pk']['uniqueID']
    ## callback status to mfast via webhook
    ExecuteBgService.postback(uniqueID=uniqueID)

    return {
        "status": True,
        "data": res['data']['update_LOS_applications_by_pk']
    }

def __send_sms(application):
    cus_name = application['LOS_customer']['fullName']
    cus_phone = application['LOS_customer_profile']['mobilePhone']
    contractNumber = application['contractNumber']
    sms_out = f"Chuc mung khoan vay cua QK {cus_name} da duoc kich hoat {contractNumber}."
    return SmsSevice.activition(cus_phone, sms_out)