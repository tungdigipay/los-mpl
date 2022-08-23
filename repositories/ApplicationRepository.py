from libraries import Hasura

def init(data):
    if data['type'] == "init":
        return __init_add(data)
    else :
        return __init_update(data)

def __init_add(data):
    query = """
    mutation m_insert_LOS_customer_ocrs_one {
        insert_LOS_customer_ocrs_one(
            object: {
                idNumberFrontImage: "%s",
                idNumberBackImage: "%s",
                status: "%s"
                responseOCR: "%s"
                LOS_application:{
                    data:{
                        statusID: %d,
                        customerID: %d,
                        LOS_customer_profile: {
                            data: {
                                idNumber_dateOfIssue: "%s",
                                idNumber_issuePlace: "%s",
                                mobilePhone: "%s",
                                nationality: "%s",
                                customerID: %d
                            }
                        }
                    }
                }
            }
        ) {
            LOS_application{ uniqueID ID}
        }
    }
    """ % (
        data['idNumberFrontImage'], data['idNumberBackImage'], data['status'], data['extractData'].replace('"', '\\"'),
        data['statusID'], data['customerID'],
        data['idNumber_dateOfIssue'], data['idNumber_issuePlace'], data['mobilePhone'], data['nationality'], data['customerID']
    )
    res = Hasura.process("m_insert_LOS_customer_ocrs_one", query)
    if res['status'] == False:
        return res
    return {
        "status": True,
        "data": res['data']['insert_LOS_customer_ocrs_one']['LOS_application']
    }

def __init_update(data):
    query = """
    mutation m_update_LOS_customer_profiles {
        update_LOS_customer_profiles(
            where: {
                LOS_applications: {
                    uniqueID: {_eq: "%s" } }
                }
            , _set: {
                email: "%s",
                marritalStatusID: %d,
                idNumber_dateOfIssue: "%s",
                idNumber_issuePlace: "%s",
            }) {
            affected_rows
        }
    }
    """ % (
        data['uniqueID'], data['email'], data['marritalStatusID'], 
        data['idNumber_dateOfIssue'], data['idNumber_issuePlace']
    )
    res = Hasura.process("m_update_LOS_customer_profiles", query)
    if res['status'] == False:
        return res
    return {
        "status": True,
        "data": {
            "uniqueID": data['uniqueID']
        }
    }

def submit(data):
    applicationID = data['applicationID']
    customerID = data['customerID']
    customer_profileID = data['customer_profileID']
    statusID = data['statusID']
    productID = data['productID']
    note = data['note']
    loanTenor = data['loanTenor']
    loanAmount = data['loanAmount']
    emi = data['emi']

    ## thông tin nơi ở
    currentAddressProvince = data['currentAddressProvince']
    currentAddressDistrict = data['currentAddressDistrict']
    currentAddressWard = data['currentAddressWard']
    currentAddressDetail = data['currentAddressDetail']

    ## thông tin hộ khẩu
    permanentAddressProvince = data['permanentAddressProvince']
    permanentAddressDistrict = data['permanentAddressDistrict']
    permanentAddressWard = data['permanentAddressWard']
    permanentAddressDetail = data['permanentAddressDetail']

    ## thông tin nghề nghiệp
    companyName = data['companyName']
    monthlyIncome = data['monthlyIncome']
    monthlyExpenses = data['monthlyExpenses']
    employmentType = data['employmentType']

    ## thông tin tham chiếu
    reference1Name = data['reference1Name']
    reference1Relationship = data['reference1Relationship']
    reference1Phone = data['reference1Phone']

    reference2Name = data['reference2Name']
    reference2Relationship = data['reference2Relationship']
    reference2Phone = data['reference2Phone']

    query = """
    mutation m_update_LOS_applications { 
        update_LOS_applications(
            where: {
                ID: { _eq: %d }
            }, 
            _set: { 
                customerID: %d, 
                customer_profileID: %d, 
                statusID: %d,

                productID: %d,
                note: "%s",
                loanTenor: %d,
                loanAmount: %d,
                emi: %d,

                companyName: "%s",
                monthlyIncome: %d,
                monthlyExpenses: %d,
                employmentType: %d,

                reference1Name: "%s",
                reference1Relationship: %d,
                reference1Phone: "%s",

                reference2Name: "%s",
                reference2Relationship: %d,
                reference2Phone: "%s",
            }
        ) {
            returning{ ID uniqueID}
        }

        update_LOS_customer_profiles (
            where: {
                ID: { _eq: %d }
            },
            _set: {
                currentAddressProvince: %d,
                currentAddressDistrict: %d,
                currentAddressWard: %d,
                currentAddressDetail: "%s",

                permanentAddressProvince: %d,
                permanentAddressDistrict: %d,
                permanentAddressWard: %d,
                permanentAddressDetail: "%s"
            }
        ){
            returning{ ID uniqueID}
        }
    } 
    """ % (
        applicationID,
        customerID, customer_profileID, statusID,
        productID, note, loanTenor, loanAmount, emi,
        companyName, monthlyIncome, monthlyExpenses, employmentType,
        reference1Name, reference1Relationship, reference1Phone,
        reference2Name, reference2Relationship, reference2Phone,

        customer_profileID,
        currentAddressProvince, currentAddressDistrict, currentAddressWard, currentAddressDetail,
        permanentAddressProvince, permanentAddressDistrict, permanentAddressWard, permanentAddressDetail
    )
    res = Hasura.process("m_update_LOS_applications", query)

    return res

def detail_by_uniqueID(uniqueID):
    query = """
    query q_LOS_applications {
        LOS_applications(
            where: {
                uniqueID: {
                    _eq: "%s" 
                }
            }
        ) {
            ID customerID customer_profileID statusID
        }
    }
    """ % (uniqueID)

    res = Hasura.process("q_LOS_applications", query)
    return res

def update_kyc(data):
    query = """
    mutation update_LOS_customer_ocrs {
        update_LOS_customer_ocrs(
            where: {
                LOS_application: { ID: { _eq: %d }}
            }, 
            _set: {
                faceImage: "%s",
                responseEkyc: "%s"
            }
        ) {
            affected_rows
        }

        LOS_applications(
            where: {
                ID: { _eq: %d }
            },
            _set: {
                statusID: 2
            }
        )
    }
    """ % (
        data['applicationID'], data['faceImage'], data['extractData'].replace('"', '\\"'),
        data['applicationID']
    )

    res = Hasura.process("update_LOS_customer_ocrs", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": {
            "uniqueID": data['uniqueID']
        }
    }