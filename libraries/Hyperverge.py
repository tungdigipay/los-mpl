import json, configparser, requests
from urllib.parse import urlencode

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['HYPERVERGE']
base_url = config['base_url']
api_id = config['app_id']
api_key = config['app_key']

def login():
    return process("/login", "POST", {
        "appId": api_id,
        "appKey": api_key,
        "expiry": 30000
    })

def process(slug, type, payload):
    url = f"{base_url}{slug}"
    payload = json.dumps(payload)
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request(type, url, headers=headers, data=payload)
    try:
        return json.loads(response.text)
    except ValueError as e:
        return {
            "status": False,
            "message": "Đã có lỗi dịch vụ từ Hyperverge"
        }