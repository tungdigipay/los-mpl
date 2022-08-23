from repositories import StatusRepository

def detail_by_id(statusID):
    return StatusRepository.detail_by_id(statusID)

def detail_application_by_unique(uniqueID):
    application = StatusRepository.detail_application_by_unique(uniqueID)
    if application == []:
        return application

    LOS_customer_profile = application['LOS_customer_profile']
    LOS_customer = application['LOS_customer']

    if LOS_customer_profile['addressFull'] == None:
        address = ""
    else:
        address = LOS_customer_profile['addressFull'] + ", "
    address += LOS_customer_profile['current_LOS_master_location_ward']['name'] + ", "
    address += LOS_customer_profile['current_LOS_master_location_district']['name'] + ", "
    address += LOS_customer_profile['current_LOS_master_location_province']['name']
    approveAmount = application['loanAmount']

    result = {
        "customerIdNumber": LOS_customer['idNumber'],
        "customerName": LOS_customer['fullName'],
        "customerPhone": LOS_customer_profile['mobilePhone'],
        "customerAddress": address,
        "partnerCode":"mpl",
        "requestAmount": application['loanAmount'],
        "contractNumber": application['contractNumber'],
        "tenor": application['loanTenor'],
        "approveAmount": approveAmount,
        "insurance": "1",
        "saleCode": "987655",
        "note": application['note'],
        "status": application['LOS_status']['alias'],
        "applicationID": application['ID']
    }
    return result