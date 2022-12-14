from helpers.CommonHelper import downloadFile
from libraries import EsignFPT
from services import EsignService, SmsService, ApplicationService, EmailService
from repositories import EsignRepository
import base64, requests

def preparing(agreementUUID):
    EsignFPT.prepareCertificateForSignCloud(agreementUUID)
    return EsignFPT.prepareFileForSignCloud(agreementUUID)

def confirm(request):
    detail = EsignRepository.detail_for_esign(request.uniqueID)
    if detail['status'] == False:
        return detail
    application = detail['data']

    agreementUUID = application['LOS_application_esign']['agreementUUID']
    BillCode = application['LOS_application_esign']['billCode']
    otpCode = request.otpCode

    res = EsignFPT.authorizeCounterSigningForSignCloud(agreementUUID, otpCode, BillCode)
    if res['status'] == False:
        return res

    res = EsignFPT.regenerateAuthorizationCodeForSignCloud(agreementUUID)
    if res['status'] == False:
        return res

    ApplicationService.update_status(application, 15, "Khách hàng ký hợp đồng thành công")
    return {
        "status": True,
        "message": "Thành công"
    }

def verify(request):
    res = EsignService.verify(request)
    if res['status'] == False:
        return res

    if res['data'] == []:
        return {
            "status": False,
            "message": "Không tìm thấy hồ sơ này"
        }
        
    data = res['data'][0]
    applicationID = data['LOS_application']['ID']
    idNumberFrontImage = data['LOS_application']['LOS_customer_ocrs'][0]['idNumberFrontImage']
    encoded_string = base64.b64encode(requests.get(idNumberFrontImage).content)
    contractFile_string = base64.b64encode(requests.get(data['contractFile']).content)

    return {
        "status": True,
        "data": {
            "contractFile": contractFile_string,
            "idNumberFrontImage": encoded_string,
            "mobilePhone": data['LOS_application']['LOS_customer_profile']['mobilePhone'],
            "uniqueID": data['LOS_application']['uniqueID']
        }
    }

def request_otp(request):
    detail = EsignRepository.detail_for_esign(request.uniqueID)
    if detail['status'] == False:
        return detail
    application = detail['data']

    if application['LOS_application_esign']['agreementUUID'] == None:
        agreementUUID = gen_agreementUUID()
    else: 
        agreementUUID = application['LOS_application_esign']['agreementUUID']

    data = {
        "applicationID": application['ID'],
        "idNumber": application['LOS_customer']['idNumber'],
        "customerName": application['LOS_customer']['fullName'],
        "customerPhone": application['LOS_customer_profile']['mobilePhone'],
        "customerEmail": application['LOS_customer_profile']['email'],
        "city": application['LOS_customer_profile']['current_LOS_master_location_province']['name'],
        "address": application['LOS_customer_profile']['currentAddressDetail'] + ", " + application['LOS_customer_profile']['current_LOS_master_location_district']['name'],
        "idNumberFrontImage": application['LOS_customer_ocrs'][0]['idNumberFrontImage'],
        "idNumberBackImage": application['LOS_customer_ocrs'][0]['idNumberBackImage'],
        "contractFile": application['LOS_application_esign']['contractFile'],
        "contractFileName": f"agreementUUID.pdf"
    }
    prepare = EsignFPT.prepareCertificateForSignCloud(agreementUUID, data)
    if prepare['status'] == False:
        return prepare

    sign = EsignFPT.prepareFileForSignCloud(agreementUUID, data)
    if sign['status'] == False:
        return sign

    EsignRepository.storage(application, {
        "otpCode": sign['data']['authorizeCredential'],
        "agreementUUID": agreementUUID,
        "billCode": sign['data']['billCode']
    })

    SmsService.esign(application['LOS_customer_profile']['mobilePhone'], sign['data']['notificationMessage'])

    return {
        "status": True,
        "data": {
            "uniqueID": request.uniqueID,
            # "sms": sign['data']['notificationMessage']
        }
    }

def gen_agreementUUID():
    from datetime import datetime
    import random, string
    today = datetime.now()
    ran = ''.join(random.choice(string.digits) for _ in range(4))
    return today.strftime("%Y%m%d%H%M%S") + ran

def email(uniqueID, email):
    detail = EsignRepository.detail_for_esign(uniqueID)
    if detail['status'] == False:
        return detail
    application = detail['data']

    # url = "https://s3-sgn09.fptcloud.com/bnpl.profiles/contract_112208260001_0969.pdf"
    # fullName = "Thanh Tùng"
    fullName = application['LOS_customer']['fullName']
    url = application['LOS_application_esign']['contractFile']
    file = downloadFile(url, "./files/email")
    EmailService.process(email, fullName, file)

    return {
        "status": True,
        "message": "Sent email successfully"
    }