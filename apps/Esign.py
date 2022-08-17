from libraries import EsignFPT
from services import EsignService
from repositories import EsignRepository
import base64, requests

def preparing(agreementUUID):
    EsignFPT.prepareCertificateForSignCloud(agreementUUID)
    return EsignFPT.prepareFileForSignCloud(agreementUUID)

def authorize(agreementUUID, otpCode, BillCode):
    EsignFPT.authorizeCounterSigningForSignCloud(agreementUUID, otpCode, BillCode)

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

    return {
        "status": True,
        "data": {
            "contractFile": data['contractFile'],
            "idNumberFrontImage": encoded_string,
            "mobilePhone": data['LOS_application']['LOS_customer_profile']['mobilePhone'],
            "uniqueID": data['LOS_application']['uniqueID']
        }
    }

def request_otp(request):
    application = EsignRepository.detail_for_esign(request.uniqueID)
    return application
    agreementUUID = gen_agreementUUID()

    EsignFPT.prepareCertificateForSignCloud(agreementUUID)
    return EsignFPT.prepareFileForSignCloud(agreementUUID)

def gen_agreementUUID():
    from datetime import datetime
    import random, string
    today = datetime.now()
    ran = ''.join(random.choice(string.digits) for _ in range(4))
    return today.strftime("%Y%m%d%H%M%S") + ran