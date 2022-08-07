from libraries import Hasura

def init(data):
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
                        statusID: 1,
                        customerID: %d,
                        LOS_customer_profile: {
                            data: {
                                idNumber_dateOfIssue: "%s",
                                idNumber_issuePlace: "%s",
                                mobilePhone: "%s",
                                nationality: "%s",
                                customerID: %d,
                                email: "%s",
                                marritalStatusID: %d
                            }
                        }
                    }
                }
            }
        ) {
            LOS_application{ uniqueID }
        }
    }

    """ % (
        data['idNumberFrontImage'], data['idNumberBackImage'], data['status'], data['extractData'].replace('"', '\\"'),
        data['customerID'],
        data['idNumber_dateOfIssue'], data['idNumber_issuePlace'], data['mobilePhone'], data['nationality'], data['customerID'], data['email'], data['marritalStatusID']
    )
    print (query)
    res = Hasura.process("m_insert_LOS_customer_ocrs_one", query)

    return res

def submit(data):
    customerID = data['customerID']
    customer_profileID = data['customer_profileID']
    statusID = data['statusID']

    query = """
    mutation m_insert_LOS_applications_one { 
        insert_LOS_applications_one(
            object: { 
                customerID: %d, 
                customer_profileID: %d, 
                statusID: %d
            }
        ) {
            ID uniqueID
        }
    } 
    """ % (customerID, customer_profileID, statusID)
    res = Hasura.process("m_insert_LOS_applications_one", query)

    return res