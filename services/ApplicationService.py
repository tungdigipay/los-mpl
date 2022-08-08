from libraries import Kalapa, MFast

def credit_score(idNumber, mobilePhone):
    return Kalapa.process("user-profile/scoring/social_fraud", "GET", {
        "id": idNumber,
        "mobile": mobilePhone
    })

def mfast_blacklist(idNumber, mobilePhone):
    return MFast.process("/blacklist", "POST", {
        "idNumber": idNumber,
        "mobilePhone": mobilePhone
    })

def mfast_dedup(idNumber, mobilePhone):
    return MFast.process("/dedup", "POST", {
        "idNumber": idNumber,
        "mobilePhone": mobilePhone
    })

def dedup_in_los(idNumber):
    
    return {
        "status": True,
        "message": "",
        "code": ""
    }