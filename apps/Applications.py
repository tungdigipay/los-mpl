from repositories import ApplicationRepository, CustomerRepository
from services import OtpService, DgpService, ApplicationService
from multiprocessing.dummy import Pool
import requests
from helpers.CommonHelper import calc_emi

def init(request):
    data = {
        "type"          : request.type,
        "uniqueID"      : request.uniqueID,
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
        "extractData"           : request.extractData,
        "statusID"              : 1
    }

    ## check otp status
    otp_data = OtpService.check_otp(request.mobilePhoneUUID)
    if otp_data['status'] == False:
        return otp_data
    mobilePhone = otp_data['data']['mobilePhone']
    data["mobilePhone"] = mobilePhone

    ## check dedup in los
    check_dedup_in_los = ApplicationService.dedup_in_los(data['idNumber'], mobilePhone)
    if check_dedup_in_los['status'] == False:
        return {
            "status": False,
            "message": check_dedup_in_los['message']
        }

    customer = CustomerRepository.create(data)
    if customer['status'] == False:
        return customer

    customerID = customer['data']['ID']
    data["customerID"] = customerID

    res = ApplicationRepository.init(data)
    if res['status'] == False:
        return res

    dgp_blacklist_result = DgpService.check_blacklist(data['idNumber'], mobilePhone)
    if dgp_blacklist_result['status'] == False:
        return dgp_blacklist_result

    ## check DGP dedup
    dgp_dedup_result = DgpService.check_dedup(data['idNumber'], mobilePhone)
    if dgp_dedup_result['status'] == False:
        return dgp_dedup_result

    return {
        "status": True,
        "data": {
            "uniqueID": res['data']['uniqueID']
        }
    }

def submit(request):
    application = ApplicationRepository.detail_by_uniqueID(request.uniqueID)
    if application['status'] == False:
        return application
    
    if application['data']['LOS_applications'] == []:
        return {
            "status": False,
            "message": "Rất tiếc không thể hoàn tất hồ sơ!"
        }

    applicationID = application['data']['LOS_applications'][0]['ID']
    customerID = application['data']['LOS_applications'][0]['customerID']
    customer_profileID = application['data']['LOS_applications'][0]['customer_profileID']

    data = {
        "applicationID": applicationID,
        "customerID": customerID, 
        "customer_profileID": customer_profileID, 
        "statusID": 3, ## Khách hàng hoàn tất hồ sơ vay và chờ xét duyệt
        "productID": 1,

        "note": request.note,
        "currentAddressProvince": request.currentAddressProvince,
        "currentAddressDistrict": request.currentAddressDistrict,
        "currentAddressWard": request.currentAddressWard,
        "currentAddressDetail": request.currentAddressDetail,

        "permanentAddressProvince": request.permanentAddressProvince,
        "permanentAddressDistrict": request.permanentAddressDistrict,
        "permanentAddressWard": request.permanentAddressWard,
        "permanentAddressDetail": request.permanentAddressDetail,

        "employmentType": request.employmentType, 
        "companyName":  request.companyName, 
        "monthlyIncome": request.monthlyIncome, 
        "monthlyExpenses": request.monthlyExpenses, 

        "bankID": request.bankID, 
        "bankAccountNumber":  request.bankAccountNumber,
        "bankAccountName":  request.bankAccountName, 
        "reference1Name":  request.reference1Name.upper(),
        "reference1Relationship": request.reference1Relationship, 
        "reference1Phone": request.reference1Phone,
        "reference2Name": request.reference2Name.upper(),
        "reference2Relationship": request.reference2Relationship, 
        "reference2Phone":  request.reference2Phone,
        "loanTenor": request.loanTenor,
        "loanAmount": request.loanAmount, 
        "emi": calc_emi(request.loanAmount, request.loanTenor)#request.emi
    }
    
    res = ApplicationRepository.submit(data)
    if res['status'] == False:
        return res

    uniqueID = res['data']['update_LOS_applications']['returning'][0]['uniqueID']
    pool = Pool(1)
    pool.apply_async(requests.get, ['https://mpl-rc.mfast.vn/applications/prescore?uniqueID=' + uniqueID])
    return {
        "status": True,
        "data": {
            "uniqueID": uniqueID
        }
    }