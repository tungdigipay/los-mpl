from libraries import Hasura

def record_log(mobilePhone, otpCode, res):
    query = """
mutation m_otp {
    insert_LOG_otp_one(
        object: {
            mobilePhone: "%s",
            otpCode: "%s",
            dataResponse: "%s"
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
    { ID createdDate dataResponse mobilePhone otpCode retryTime } 
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