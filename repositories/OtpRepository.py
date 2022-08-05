from libraries import Hasura

def record_log(mobilePhone, otpCode, res):
    query = 'mutation m_otp{insert_LOG_otp_one(object:{mobilePhone:"' + mobilePhone + '",otpCode:"' + otpCode + '", dataResponse:"' + res + '"}) { UUID }}'
    responseInsert = Hasura.process("m_otp", query)

    return {
        'status': True,
        'data': responseInsert['data']['insert_LOG_otp_one']
    }