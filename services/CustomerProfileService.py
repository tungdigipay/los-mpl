from libraries import Hasura

def create(data):
    idNumber_dateOfIssue = data['idNumber_dateOfIssue']
    idNumber_issuePlace = data['idNumber_issuePlace']
    email = data['email']
    marritalStatusID = data['marritalStatusID']
    nationality = "Việt Nam"
    mobilePhone = data['mobilePhone']
    customerID = data['customerID']

    query = """
mutation m_insertCustomerProfile { 
    insert_LOS_customer_profiles(
        objects: {
            idNumber_dateOfIssue: "%s", 
            idNumber_issuePlace: "%s", 
            email: "%s", 
            marritalStatusID: %d,
            nationality: "%s",
            mobilePhone: "%s",
            customerID: %d
        }
    ) 
    { returning { ID uniqueID } } 
} 
""" % (idNumber_dateOfIssue, idNumber_issuePlace, email, marritalStatusID, nationality, mobilePhone, customerID)
    res = Hasura.process("m_insertCustomerProfile", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }
    
    return {
        "status": True,
        "data": res['data']['insert_LOS_customer_profiles']['returning'][0]
    }