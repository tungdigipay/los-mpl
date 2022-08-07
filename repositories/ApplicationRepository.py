from libraries import Hasura

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