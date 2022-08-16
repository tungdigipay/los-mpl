from repositories import OtpRepository
from services import ApplicationService

def preparing(application):
    ApplicationService.update_status(application, 14 , "Đã sinh hợp đồng và chờ khách hàng ký")
    return {
        "status": True,
        "message": "Đã sinh hợp đồng và chờ khách hàng ký"
    }

def verify(request):
    return {
        "status": True,
        "data": {
            'contractLink': "/files/esign/contract.signed.pdf"
        }
    }

def otp(request):
    return OtpRepository.record_log(request.mobilePhone, request.otpCode, "successful")

def process(request):
    return {
        "status": True,
        "message": "Thành công"
    }