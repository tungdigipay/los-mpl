import json, configparser, requests

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['HASURA']
endpoint = config['endpoint']
secret = config['secret']

def process(name, query, variables: dict = {}):

    headers = {
        'content-type': 'application/json',
        'x-hasura-admin-secret': secret
    }

    data = {
        "operationName": name,
        "query": query,
        "variables": variables
    }
    response = requests.post(endpoint, headers = headers, data=json.dumps(data))
    status_code = response.status_code
    res = response.json()
    
    if "errors" in res:
        return {
            'status': False,
            'message': res['errors'][0]['message']
        }

    if status_code != 200:
        return {
            'status': False,
            'message': "Đã có lỗi từ Hasura"
        }

    return {
        'status': True,
        'data': res['data']
    }