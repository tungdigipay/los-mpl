from services import ApplicationService  

def check_blacklist(idNumber, mobilePhone):
    res = ApplicationService.mfast_blacklist(idNumber, mobilePhone)
    return res

def check_dedup(idNumber, mobilePhone):
    res = ApplicationService.mfast_dedup(idNumber, mobilePhone)
    return res