from fastapi import applications
from repositories import StatusRepository
from services import StatusService
from libraries import MFast

def status(uniqueID):
    application = StatusService.detail_application_by_unique(uniqueID)
    if application == []:
        return {
            "status": False,
            "message": "Hồ sơ không tồn tại"
        }

    return MFast.process("/mfast_api_v1/mpl/loans", "POST", application)