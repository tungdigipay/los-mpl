from libraries import EsignFPT
from services import EsignService
import base64, requests

def preparing(agreementUUID):
    EsignFPT.prepareCertificateForSignCloud(agreementUUID)
    return EsignFPT.prepareFileForSignCloud(agreementUUID)

def authorize(agreementUUID, otpCode, BillCode):
    EsignFPT.authorizeCounterSigningForSignCloud(agreementUUID, otpCode, BillCode)

def verify(request):
    ## sample data 
    idNumberFrontImage = "https://s3-sgn09.fptcloud.com/appay.cloudcms/20220816140335zmt59khvfi.jpg"
    encoded_string = base64.b64encode(requests.get(idNumberFrontImage).content)
    return {
        "status": True,
        "data": {
            "contractFile": "/files/esign/contract.signed.pdf",
            "idNumberFrontImage": encoded_string
        }
    }

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
            "idNumberFrontImage": encoded_string
        }
    }

def request_otp():
    pass