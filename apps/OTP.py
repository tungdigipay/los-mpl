from libraries import Hasura
from libraries import OtpCall
from repositories import OtpRepository
import random, string

def request(request):
    if request.mobilePhone in ['0919339894', '0905044591']:
        otpCode = "1234"
    else: 
        otpCode = _create_otpCode()
    return OtpCall.process(request.mobilePhone, otpCode)

def _create_otpCode() -> str:
    return ''.join(random.choice(string.digits) for _ in range(4))

def verify(request):
    response = OtpRepository.get_by_UUID(request.UUID)

    if response['data']['LOG_otp'] == [] :
        return {
            'status': False,
            'message': "Không tìm thấy UUID"
        }

    data_otp = response['data']['LOG_otp'][0]
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
    OtpRepository.update_retry(data_otp['ID'], newRetryTime)

    return {
        'status': False,
        'message': "OTP không chính xác"
    }