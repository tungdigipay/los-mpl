from repositories import CustomerRepository
from services import OtpService, DgpService, CustomerOcrService, CustomerProfileService

def storage(request):
    data = {
        "mobilePhoneUUID" : request.mobilePhoneUUID,
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
    otp_data = OtpService.check_otp(data['mobilePhoneUUID'])
    if otp_data['status'] == False:
        return otp_data
    mobilePhone = otp_data['data']['mobilePhone']
    data["mobilePhone"] = mobilePhone

    ## check DGP blacklist
    dgp_blacklist_result = DgpService.check_blacklist()
    if dgp_blacklist_result['status'] == False:
        return dgp_blacklist_result

    ## check DGP dedup
    dgp_dedup_result = DgpService.check_dedup()
    if dgp_dedup_result['status'] == False:
        return dgp_dedup_result

    customer = CustomerRepository.create(data)
    if customer['status'] == False:
        return customer

    customerID = customer['data']['ID']
    data["customerID"] = customerID

    customerProfile = CustomerProfileService.create(data)
    if customerProfile['status'] == False:
        return customerProfile

    data["customer_profileID"] = customerProfile['data']['ID']
    customerOCR = CustomerOcrService.create(data)
    if customerOCR['status'] == False:
        return customerOCR

    return {
        "status": True,
        "data": {
            "uniqueID": customerProfile['data']['uniqueID']
        }
    }