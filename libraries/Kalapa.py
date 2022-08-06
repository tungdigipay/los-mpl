import json, configparser, requests
from urllib.parse import urlencode
from libraries import Hasura

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['KALAPA']
base_url = config['base_url']
secret_key = config['secret_key']

def process(slug, type, payload):
    url = f"{base_url}/{slug}"
    headers = {
    'Authorization': f'Bearer {secret_key}'
    }

    if type == "GET":
        url += "?" + urlencode(payload)

    response = requests.request(type, url, headers=headers, data=payload)
    query = """
mutation m_log_kalapa { 
    insert_LOG_kalapa(
        objects: {
            url: "%s", 
            payload: "%s", 
            response: "%s"
        }
    ) { 
        returning { ID } 
    } 
}
    """ % (url, json.dumps(payload).replace('"', '\\"'), response.text.replace('"', '\\"'))
    Hasura.process("m_log_kalapa", query)

    try:
        response = json.loads(response.text)
        return {
            "status": True,
            "data": response
        }
    except ValueError as e:
        return {
            "status": False,
            "message": response
        }
