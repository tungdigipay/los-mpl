from libraries import Hasura

def create(data):
    fullName = data['fullName'].upper()
    dateOfBirth = data['dateOfBirth']
    genderID = data['genderID']
    idNumber = data['idNumber']

    ## check exist customer
    check_exist = get_by_idNumber(idNumber)
    if check_exist['status'] == False:
        return check_exist

    if check_exist['data']['LOS_customers'] == []:
        query = """
        mutation m_insertCustomer { 
            insert_LOS_customers(
                objects: {
                    dateOfBirth: "%s", 
                    fullName: "%s", 
                    idNumber: "%s", 
                    genderID: %d
                }
            ) 
            { returning { ID uniqueID } } 
        } 
        """ % (dateOfBirth, fullName, idNumber, genderID)
        res = Hasura.process("m_insertCustomer", query)
        if res['status'] == False:
            return {
                "status": False,
                "message": res['message']
            }
        responseCustomer = res['data']['insert_LOS_customers']['returning'][0]

    else:
        customerID = check_exist['data']['LOS_customers'][0]['ID']
        query = """
        mutation m_updateCustomer { 
            update_LOS_customers_by_pk(
                pk_columns: { ID: %d }, 
                _set: {
                    dateOfBirth: "%s", 
                    fullName: "%s", 
                    idNumber: "%s", 
                    genderID: %d
                }
            ) {
                ID uniqueID
            }
        }
        """ % (customerID, dateOfBirth, fullName, idNumber, genderID)
        res = Hasura.process("m_updateCustomer", query)
        if res['status'] == False:
            return {
                "status": False,
                "message": res['message']
            }
        responseCustomer = res['data']['update_LOS_customers_by_pk']
    
    return {
        "status": True,
        "data": responseCustomer
    }

def get_by_idNumber(idNumber):
    query = """
    query get_by_idNumber { 
        LOS_customers (
            where: {
                idNumber: {_eq: "%s"} }
        ) 
        { ID } 
    }
    """ % (idNumber)
    return  Hasura.process("get_by_idNumber", query)
