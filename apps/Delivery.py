from services import DeliveryService

def order(uniqueID):
    return DeliveryService.order(uniqueID)

def packing(uniqueID):
    return DeliveryService.packing(uniqueID)

def shipping(uniqueID):
    return DeliveryService.shipping(uniqueID)

def delivered(uniqueID):
    return DeliveryService.delivered(uniqueID)