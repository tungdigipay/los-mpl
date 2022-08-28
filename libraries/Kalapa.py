import json, configparser, requests
from urllib.parse import urlencode
from libraries import Hasura
from helpers import CommonHelper

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['KALAPA']
base_url = config['base_url']
secret_key = config['secret_key']

def process(slug, type, payload, function):
    exist = check_exist(payload, function=function)
    if exist != []:
        return {
            "status": True,
            "data": exist['response'],
            "logID": exist['ID']
        }

    url = f"{base_url}/{slug}"
    headers = {
    'Authorization': f'Bearer {secret_key}'
    }

    if type == "GET":
        url += "?" + urlencode(payload)

    logID = __insert(url, function, payload)
    response = requests.request(type, url, headers=headers, data=payload)

    try:
        response = json.loads(response.text)
        __update(logID, response)
        return {
            "status": True,
            "data": response,
            "logID": logID
        }
    except ValueError as e:
        return {
            "status": False,
            "message": response.text,
            "logID": logID
        }

def check_exist(payload, function):
    thirty_days_ago = CommonHelper.thirty_days_ago()
    query = """
    query m_exist_LOG_kalapa($payload: jsonb = "") {
        LOG_kalapa(
            where: {
                payload: { _contains: $payload }, 
                createdDate: {_gt: "%s"}, 
                function: {_eq: "%s"}
            }, 
            order_by: {createdDate: desc}
        ) {
            ID response payload createdDate
        }
    }
    """ % (thirty_days_ago, function)
    variables = {
        "payload": payload
    }
    res = Hasura.process("m_exist_LOG_kalapa", query, variables)

    if res['status'] == False:
        return []
    if res['data']['LOG_kalapa'] == []:
        return []

    return res['data']['LOG_kalapa'][0]

def __insert(url, function, payload):
    variables = {
        "payload": payload
    }
    query = """
        mutation m_log_kalapa($payload: jsonb = "") { 
            insert_LOG_kalapa(
                objects: {
                    url: "%s", 
                    payload: $payload, 
                    function: "%s"
                }
            ) { 
                returning { ID } 
            } 
        }
    """ % (url, function)

    res = Hasura.process("m_log_kalapa", query, variables)
    return res['data']['insert_LOG_kalapa']['returning'][0]['ID']

def __update(logID, response):
    variables = {
        "response": response
    }
    query = """
    mutation m_log_kalapa($response: jsonb = "") {
        update_LOG_kalapa_by_pk(
            pk_columns: { ID: %d }, 
            _set: {
                response: $response
            }
        ) {
            ID
        }
    }
    """ % (logID)
    res = Hasura.process("m_log_kalapa", query, variables)
    return res