from repositories import OtpRepository
def verify(request):
    return {
        "status": True,
        "data": {
            'contractLink': "/files/esign/contract.signed.pdf"
        }
    }

def otp(request):
    otpCode = "123456"
    return OtpRepository.record_log("0905044591", otpCode, "successful")

def process(request):
    return {
        "status": True,
        "message": "Thành công"
    }