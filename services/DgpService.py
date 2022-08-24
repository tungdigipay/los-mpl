from services import ApplicationService, ScoringLogService

def check_blacklist(applicationID, idNumber, mobilePhone):
    res = ApplicationService.mfast_blacklist(idNumber, mobilePhone)

    payload = {
        "idNumber": idNumber, 
        "mobilePhone": mobilePhone
    }

    result_content = {}
    result_content["message"] = res['message']
    if res['status'] == True: 
        result = "pass" 
    else: 
        result = "rejected"
    
    ScoringLogService.record({
        "applicationID": applicationID, 
        "result": result, 
        "type": "dgp_blacklist", 
        "label": "DGP Blacklist", 
        "logServiceID": 0
    }, payload, result_content)
    
    return res

def check_dedup(idNumber, mobilePhone):
    res = ApplicationService.mfast_dedup(idNumber, mobilePhone)
    return res