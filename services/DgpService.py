from services import ApplicationService

def check_blacklist(applicationID, idNumber, mobilePhone):
    return ApplicationService.mfast_blacklist(applicationID, idNumber, mobilePhone)

def check_dedup(idNumber, mobilePhone):
    res = ApplicationService.mfast_dedup(idNumber, mobilePhone)
    return res

def gotit():
    pass