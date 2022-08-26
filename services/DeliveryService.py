from services import ExecuteBgService, ApplicationService
from repositories import DeliveryRepository
from libraries import MFast

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

    __gotit_request(application)

    ApplicationService.update_status(application, 18, '')
    ExecuteBgService.delivery(uniqueID, "packing")
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
    ExecuteBgService.delivery(uniqueID, "shipping")
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
    ExecuteBgService.delivery(uniqueID, "delivered")
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
    ExecuteBgService.activition(uniqueID)
    return {
        "status": True,
        "message": "Thành công"
    }

def __gotit_request(application):
    res = MFast.process("gotit", "POST", {
        "receiverName": application['LOS_customer']['fullName'],
        "receiverPhone": application['LOS_customer_profile']['mobilePhone'],
        "receiverEmail": application['LOS_customer_profile']['email'],
        "senderName": application['LOS_customer']['fullName'],
        "message": "",
        "priceId":"10730",
        "productId":"2206",
        "partnerCode":"mpl"
    })

    if res['status'] == False:
        return res

    voucherCode = res['data']['code']