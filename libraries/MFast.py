import json, configparser, requests
from urllib.parse import urlencode
from libraries import Hasura

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['MFAST']
base_url = config['base_url']
basic_username = config['basic_username']
basic_password = config['basic_password']

def process(slug, type, payload):
    url = f"{base_url}/{slug}"

    payload = json.dumps(payload)
    headers = {
    # 'Authorization': 'Basic bWZhc3Q6SlA1MEF1MERHVA==',
    'Content-Type': 'application/json'
    }
    response = requests.request(
        type, 
        url, 
        headers=headers, 
        data=payload, 
        auth=(basic_username, basic_password)
    )
    try:
        return json.loads(response.text)
    except ValueError as e:
        return {
            "status": False,
            "message": "Đã có lỗi dịch vụ từ DGP"
        }

def __log(data, logID=None):
    objects = create_objects(data)
    if logID == None:
        query = """
        mutation m_LOG_mfast_service{
            insert_LOG_mfast_service_one(
                object: {
                    %s
                }
            ) {
                ID
            }
        }
        """ % (
            objects
        )
        variables = {
            "payload": data['payload']
        }
    else:
        query = """
        mutation m_LOG_mfast_service ($response: ) {
            update_LOG_mfast_service_by_pk(
                pk_columns: { ID: %d }, _set: { 
                    response: $response
                }
            ) {
                ID
            }
        }
        """ % (
            logID, objects
        )
        variables = {
            "response": data['response']
        }
    res = Hasura.process("m_LOG_mfast_service", query, variables)
    if res['status'] == False:
        return res

    return {
        "status": True,
        "data": {
            "ID": ID
        }
    }

def create_objects(data):
    objects = ""
    if 'url' in data:
        objects += 'url: "%s", ' % (data['url'])

    return objects