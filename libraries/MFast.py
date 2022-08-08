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