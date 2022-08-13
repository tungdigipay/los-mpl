import configparser, requests
from repositories import OtpRepository
from libraries import Hasura

config = configparser.ConfigParser()
config.read('configs.ini')
configOTP = config['SMS']

def process(mobilePhone, sms_out):
    u = configOTP['username']
    p = configOTP['pwd']
    f = configOTP['from']
    endpoint = configOTP['endpoint']
    url = f'{endpoint}/?u={u}&pwd={p}&from={f}&phone={mobilePhone}&sms={sms_out}'

    log_res = __save_log(url)
    if log_res['status'] == False:
        return log_res

    logID = log_res['data']['ID']
    
    response = requests.get(url)
    status_code = response.status_code
    res = response.text
    
    __update_log(res, logID)
    return {
        "status": True,
        "data": res
    }

def __save_log(url):
    query = """
    mutation m_insert_LOG_sms {
    insert_LOG_sms(
            objects: {url: "%s"}
        ) {
            returning { ID }
        }
    }
    """ % (url)
    res = Hasura.process("m_insert_LOG_sms", query)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": res['data']['insert_LOG_sms']['returning'][0]
    }

def __update_log(response, logID):
    query = """
    mutation m_update_LOG_sms_by_pk {
        update_LOG_sms_by_pk(
            pk_columns: { ID: %d }, _set: {response: "%s"}
        ) { ID }
    }
    """ % (logID, response)
    return Hasura.process("m_update_LOG_sms_by_pk", query)