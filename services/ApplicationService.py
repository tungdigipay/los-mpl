from libraries import Kalapa, MFast, Hasura

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
    acting = __check_dedup_in_los_acting(idNumber)
    if acting['status'] == False:
        return acting

    processing = __check_dedup_in_los_processing(idNumber)
    if processing['status'] == False:
        return processing

    return {
        "status": True,
        "message": "",
        "code": ""
    }

def __check_dedup_in_los_acting(idNumber):
    query = """
    query q_LOS_applications_aggregate {
        LOS_applications_aggregate(
            where: {statusID: { _eq: 23 }, 
            LOS_customer: { idNumber: { _eq: "%s" } } }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (idNumber)
    res = Hasura.process("q_LOS_applications_aggregate", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }
    
    if (res['data']['LOS_applications_aggregate']['aggregate']['count'] > 1):
        return {
            "status": False,
            "message": "Có hơn 1 khoản vay BNPL đang hoạt động",
            "code": "DDP_LCT1"
        }
    
    return {
        "status": True
    }

def __check_dedup_in_los_processing(idNumber):
    query = """
    query q_LOS_applications_aggregate {
        LOS_applications_aggregate(
            where: {statusID: { _eq: 23 }, 
            LOS_customer: { idNumber: { _eq: "%s" } } }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (idNumber)
    res = Hasura.process("q_LOS_applications_aggregate", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }
    
    if (res['data']['LOS_applications_aggregate']['aggregate']['count'] > 1):
        return {
            "status": False,
            "message": "Có hơn 1 khoản vay BNPL đang hoạt động",
            "code": "DDP_LCT1"
        }
    
    return {
        "status": True
    }

def __check_dedup_in_los_refused(idNumber):
    query = """
    query q_LOS_applications_aggregate {
        LOS_applications_aggregate(
            where: { statusID : { _in: [5, 9, 11, 17] }, 
            LOS_customer: { idNumber: { _eq: "%s" } } }
        ) {
            aggregate {
                count
            }
        }
    }
    """ % (idNumber)
    res = Hasura.process("q_LOS_applications_aggregate", query)
    if res['status'] == False:
        return {
            "status": False,
            "message": res['message']
        }
    
    if (res['data']['LOS_applications_aggregate']['aggregate']['count'] > 0):
        return {
            "status": False,
            "message": "Có khoản vay BNPL bị từ chối dưới 30 ngày",
            "code": "DDP_LCT3"
        }
    
    return {
        "status": True
    }