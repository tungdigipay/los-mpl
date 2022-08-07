
def storage(request):
    data = {
        "uniqueID"      : request.uniqueID,
        "faceImage"     : request.faceImage,
        "extractData"   : request.extractData,
    }

    return {
        "status": True,
        "data": {
            "uniqueID": data['uniqueID']
        }
    }