from services import StatusService
from libraries import MFast

def status(uniqueID):
    application = StatusService.detail_application_by_unique(uniqueID)
    if application == []:
        return {
            "status": False,
            "message": "Hồ sơ không tồn tại"
        }

    return MFast.process("loans", "POST", application)