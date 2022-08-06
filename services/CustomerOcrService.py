from libraries import Hasura

def create(data):
    customer_profileID = data['customer_profileID']
    idNumberFrontImage = data['idNumberFrontImage']
    idNumberBackImage = data['idNumberBackImage']
    status = data['status']
    responseOCR = data['extractData']

    query = """
    mutation m_insertCustomerOcr { 
        insert_LOS_customer_ocrs(
            objects: {
                customer_profileID: %d, 
                idNumberFrontImage: "%s", 
                idNumberBackImage: "%s", 
                status: "%s",
                responseOCR: "%s"
            }
        ) 
        { returning { ID } } 
    } 
    """ % (customer_profileID, idNumberFrontImage, idNumberBackImage, status, responseOCR.replace('"', '\\"'))
    print (query)
    res = Hasura.process("m_insertCustomerOcr", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }

    return {
        "status": True,
        "data": res['data']['insert_LOS_customer_ocrs']['returning'][0]
    }