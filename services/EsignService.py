from repositories import OtpRepository, EsignRepository
from services import SmsSevice
from libraries import Hasura
import random, string

def preparing(application):
    contract_number = __gen_contract_number(application)

    note = "Đã sinh hợp đồng và chờ khách hàng ký"
    esignPwd = __create_pwd()
    __update_application(application, {
        "statusID": 14,
        "note": note,
        "contractNumber": contract_number
    })

    EsignRepository.storage(application, {
        'esignPwd': esignPwd,
        "contractFile": "https://s3-sgn09.fptcloud.com/appay.cloudcms/contract_template.pdf"
    })

    __send_sms(application, contract_number)
    return {
        "status": True,
        "message": "Đã sinh hợp đồng và chờ khách hàng ký"
    }

def verify(request):
    res = EsignRepository.verify_application(request.contractNumber, request.idNumber, request.password)
    return res

def otp(request):
    return OtpRepository.record_log(request.mobilePhone, request.otpCode, "successful")

def process(request):
    return {
        "status": True,
        "message": "Thành công"
    }

def __gen_contract_number(application):
    from datetime import date
    today = date.today()

    applicationID = application['ID']
    applicationID_text = str(applicationID)
    if applicationID > 10000: applicationID_text = applicationID_text[-4:len(applicationID_text)]
    else: applicationID_text = applicationID_text.zfill(4)

    contract_number = "11" + today.strftime("%y%m%d") + applicationID_text
    return contract_number

def __update_application(application, data):
    appID = application['ID']
    objects = create_objects(data)
    query = """
    mutation m_update_LOS_applications_by_pk {
        update_LOS_applications_by_pk(
            pk_columns: { ID: %d }, 
            _set: { %s }
        ) {
            ID
        }
    }
    """ % (appID, objects)

    res = Hasura.process("m_update_LOS_applications_by_pk", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }

    return {
        "status": True
    }

def create_objects(data) -> str:
    objects = ""
    if 'statusID' in data:
        objects += "statusID: %d, " % (data['statusID'])
    if 'note' in data:
        objects += 'note: "%s", ' % (data['note'])
    if 'contractNumber' in data:
        objects += 'contractNumber: "%s", ' % (data['contractNumber'])

    return objects

def __send_sms(application, contract_number):
    mobilePhone = application['LOS_customer_profile']['mobilePhone']
    link = "tai day"
    SmsSevice.approve(mobilePhone, contract_number, link)

def __create_pwd() -> str:
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))