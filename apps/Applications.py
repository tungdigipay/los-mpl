from repositories import ApplicationRepository, CustomerRepository
from services import OtpService, DgpService, CustomerOcrService, CustomerProfileService

def init(request):
    data = {
        "nationality"   : "Việt Nam",
        "fullName"      : request.fullName,
        "dateOfBirth"   : request.dateOfBirth,
        "genderID"      : request.genderID,
        "idNumber"      : request.idNumber,
        "idNumber_dateOfIssue"  : request.idNumber_dateOfIssue,
        "idNumber_issuePlace"   : request.idNumber_issuePlace,
        "email"                 : request.email,
        "marritalStatusID"      : request.marritalStatusID,
        "status"                : request.status,
        "idNumberFrontImage"    : request.idNumberFrontImage,
        "idNumberBackImage"     : request.idNumberBackImage,
        "extractData"           : request.extractData
    }

    ## check otp status
    otp_data = OtpService.check_otp(request.mobilePhoneUUID)
    if otp_data['status'] == False:
        return otp_data
    mobilePhone = otp_data['data']['mobilePhone']
    data["mobilePhone"] = mobilePhone

    customer = CustomerRepository.create(data)
    if customer['status'] == False:
        return customer

    customerID = customer['data']['ID']
    data["customerID"] = customerID

    res = ApplicationRepository.init(data)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": {
            "uniqueID": res['data']['insert_LOS_customer_ocrs_one']['LOS_application']['uniqueID']
        }
    }

def submit(data):
    data = {
        "customerID": 23, 
        "customer_profileID": 13, 
        "statusID": 1
    }
    
    res = ApplicationRepository.submit(data)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": {
            "uniqueID": res['data']['insert_LOS_applications_one']['uniqueID']
        }
    }