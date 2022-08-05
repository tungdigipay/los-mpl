from libraries import Hasura

def record_log(mobilePhone, otpCode, res):
    query = 'mutation m_otp{insert_LOG_otp_one(object:{mobilePhone:"' + mobilePhone + '",otpCode:"' + otpCode + '", dataResponse:"' + res + '"}) { UUID }}'
    responseInsert = Hasura.process("m_otp", query)

    return {
        'status': True,
        'data': responseInsert['data']['insert_LOG_otp_one']
    }

def get_by_UUID(UUID):
    query = 'query getUUID { LOG_otp(where: {UUID: {_eq: "' + UUID + '"} }) { ID createdDate dataResponse mobilePhone otpCode retryTime } }'
    return Hasura.process("getUUID", query)

def update_retry(ID, newRetryTime):
    query = 'mutation updateOTPRetryTime { update_LOG_otp(where: {ID: {_eq: ' + str(ID) + '} }, _set: {retryTime: "' + str(newRetryTime) + '"}) { returning { ID } } }'
    return Hasura.process("updateOTPRetryTime", query)