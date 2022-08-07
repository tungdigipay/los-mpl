from repositories import ApplicationRepository

def storage(request):
    data = {
        "uniqueID"      : request.uniqueID,
        "faceImage"     : request.faceImage,
        "extractData"   : request.extractData,
    }

    appDetail = ApplicationRepository.detail_by_uniqueID(request.uniqueID)
    if (appDetail['status'] == False):
        return {
            "status": False,
            "message": "Application not found"
        }

    data['applicationID'] = appDetail['data']['LOS_applications'][0]['ID']
    return ApplicationRepository.update_kyc(data)