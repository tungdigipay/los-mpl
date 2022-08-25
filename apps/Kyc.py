import json
from repositories import ApplicationRepository
from services import ApplicationService

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
    
    if appDetail['data']['LOS_applications'] == []:
        return {
            "status": False,
            "message": "Application not found!"
        }

    extractData = json.loads(data['extractData'])
    data['extractData'] = json.dumps(extractData)

    data['applicationID'] = appDetail['data']['LOS_applications'][0]['ID']
    res = ApplicationRepository.update_kyc(data)
    ApplicationService.update_status(appDetail['data']['LOS_applications'][0], 2, '')
    return res