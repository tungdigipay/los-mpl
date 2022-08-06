from repositories import OtpRepository

def check_otp(UUID) -> bool:
    response = OtpRepository.get_by_UUID(UUID)
    if response['data']['LOG_otp'] == [] :
        return {
            "status": False,
            "message": "Xác thực OTP không hợp lệ"
        }

    data_otp = response['data']['LOG_otp'][0]
    if data_otp['status'] != 'pass':
        return {
            "status": False,
            "message": "Xác thực OTP không hợp lệ"
        }

    return {
        "status": True,
        "data": data_otp
    }