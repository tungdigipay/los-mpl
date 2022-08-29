from fastapi import applications
from services import ActivitionService, ApplicationService, ExecuteBgService, SmsService
from datetime import datetime
from libraries import Hasura
from helpers.CommonHelper import format_money

def process(uniqueID):
    application = detail_application(uniqueID=uniqueID)
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
    res = update_activition(applicationID)
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
    emi = format_money(application['emi'], 'vnd')
    dateOfFirstPayment = application['dateOfFirstPayment']
    phoneSupport = ""
    emailSupport = "hotro-mpl@mfast.vn"
    sms_out = f"Xin chuc mung! Ho so tra cham so {contractNumber} cua {cus_name} da hoan tat. Ky thanh toan dau tien: ngay {dateOfFirstPayment} la: {emi}. Ho tro: {phoneSupport} - {emailSupport}"
    return SmsService.activition(cus_phone, sms_out)

def detail_application(uniqueID):
    query = """
    query detail_LOS_applications {
        LOS_applications(
            where: { 
                uniqueID: { _eq: "%s" } 
            }
        ) {
            ID
            LOS_customer {
                fullName
            }
            emi
            LOS_customer_profile {
                mobilePhone
            }
            loanTenor
            statusID
            dateOfFirstPayment
        }
    }
    """ % (uniqueID)
    res = Hasura.process("detail_LOS_applications", query)
    if res['status'] == False:
        return res

    if res['data']['LOS_applications'] == []:
        return {
            "status": False,
            "message": "Có lỗi hồ hơ"
        }
    
    return {
        "status": True,
        "data": res['data']['LOS_applications'][0]
    }