from libraries import Hasura
from libraries import OtpCall
import random, string

def request(request):
    otpCode = _create_otpCode()
    return OtpCall.process(request.mobilePhone, otpCode)

def _create_otpCode() -> str:
    return ''.join(random.choice(string.digits) for _ in range(4))

def verify(request):
    query = 'query getUUID { otp_logs(where: {UUID: {_eq: "' + request.UUID + '"} }) { ID createdDate dataResponse mobilePhone otpCode retryTime } }'
    response = Hasura.process("getUUID", query)

    if response['data']['otp_logs'] == [] :
        return {
            'status': False,
            'message': "Không tìm thấy UUID"
        }

    data_otp = response['data']['otp_logs'][0]
    if (data_otp['otpCode'] == request.otpCode):
        return {
            'status': True,
            'message': "Mã OTP hợp lệ"
        }

    if data_otp['retryTime'] >= 3:
        return {
            'status': True,
            'message': "Mã OTP hết hạn"
        }

    newRetryTime = data_otp['retryTime'] + 1
    query = 'mutation updateOTPRetryTime { update_otp_logs(where: {ID: {_eq: ' + str(data_otp['ID']) + '} }, _set: {retryTime: "' + str(newRetryTime) + '"}) { returning { ID } } }'
    Hasura.process("updateOTPRetryTime", query)

    return {
        'status': False,
        'message': "OTP không chính xác"
    }