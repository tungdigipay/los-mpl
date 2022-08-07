from libraries import Hasura

def record_log(mobilePhone, otpCode, res):
    query = """
mutation m_otp {
    insert_LOG_otp_one(
        object: {
            mobilePhone: "%s",
            otpCode: "%s",
            dataResponse: "%s",
            status: "new"
        }
    ) 
    { UUID }
}
    """ % (mobilePhone, otpCode, res)
    responseInsert = Hasura.process("m_otp", query)

    return {
        'status': True,
        'data': responseInsert['data']['insert_LOG_otp_one']
    }

def get_by_UUID(UUID):
    query = """
query getUUID { 
    LOG_otp (
        where: {
            UUID: {_eq: "%s"} }
    ) 
    { ID createdDate dataResponse mobilePhone otpCode retryTime status } 
}
""" % (UUID)
    return Hasura.process("getUUID", query)

def update_retry(ID, newRetryTime):
    query = """
mutation updateOTPRetryTime { 
    update_LOG_otp (
        where: {
            ID: { _eq: %d} 
        }, 
        _set: {
            retryTime: "%d"
        }
    ) 
    { returning { ID } } 
}
""" % (ID, newRetryTime)
    return Hasura.process("updateOTPRetryTime", query)

def update_status(ID, status):
    query = """
mutation updateOTPRetryTime { 
    update_LOG_otp (
        where: {
            ID: { _eq: %d} 
        }, 
        _set: {
            status: "%s"
        }
    ) 
    { returning { ID } } 
}
""" % (ID, status)
    return Hasura.process("updateOTPRetryTime", query)
