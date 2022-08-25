from services import ExecuteBgService, ApplicationService
from repositories import DeliveryRepository

def order(uniqueID):
    application = DeliveryRepository.detail_application(uniqueID=uniqueID)
    if application == []:
        return {
            "status": False,
            "message": "Không tìm thấy hồ sơ"
        }

    if application['statusID'] != 15:
        return {
            "status": False,
            "message": "Hồ sơ chưa đủ điều kiện xử lý"
        }

    ApplicationService.update_status(application, 18, '')
    return {
        "status": True,
        "message": "Thành công"
    }

def packing(uniqueID):
    application = DeliveryRepository.detail_application(uniqueID=uniqueID)
    if application == []:
        return {
            "status": False,
            "message": "Không tìm thấy hồ sơ"
        }

    ApplicationService.update_status(application, 20, '')
    return {
        "status": True,
        "message": "Thành công"
    }

def shipping(uniqueID):
    application = DeliveryRepository.detail_application(uniqueID=uniqueID)
    if application == []:
        return {
            "status": False,
            "message": "Không tìm thấy hồ sơ"
        }

    ApplicationService.update_status(application, 21, '')
    return {
        "status": True,
        "message": "Thành công"
    }

def delivered(uniqueID):
    application = DeliveryRepository.detail_application(uniqueID=uniqueID)
    if application == []:
        return {
            "status": False,
            "message": "Không tìm thấy hồ sơ"
        }

    ApplicationService.update_status(application, 22, '')
    return {
        "status": True,
        "message": "Thành công"
    }