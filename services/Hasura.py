import json, configparser, requests
from io import BytesIO

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['HASURA']
endpoint = config['endpoint']
secret = config['secret']

def process(name, query, variables: dict = {}):
    data_response = BytesIO()
    # # c = pycurl.Curl()
    # c.setopt(c.URL, endpoint)

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

    if status_code != 200:
        return {
            'status': False,
            'message': "Đã có lỗi từ Hasura"
        }

    return {
        'status': True,
        'data': res['data']
    }

if __name__ == "__main__":
    print(process("otp", "query otp { otp_logs { createdDate mobilePhone otpCode } }"))