from repositories import ApplicationRepository

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