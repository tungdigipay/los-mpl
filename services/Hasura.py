import pycurl, json, configparser
from io import BytesIO

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['HASURA']
endpoint = config['endpoint']
secret = config['secret']

def process(name, query, variables: dict = {}):
    data_response = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, endpoint)

    headers = [
        'content-type: application/json',
        f'x-hasura-admin-secret: {secret}'
    ]

    data = {
        "operationName": name,
        "query": query,
        "variables": variables
    }
    
    c.setopt(pycurl.HTTPHEADER, headers)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, json.dumps(data))
    c.setopt(c.WRITEDATA, data_response)
    c.perform()
    status_code = c.getinfo(c.RESPONSE_CODE)
    c.close()

    if status_code != 200:
        return {
            'status': False,
            'message': "Đã có lỗi từ Hasura"
        }

    get_body = data_response.getvalue()
    res = json.loads(get_body.decode('utf8'))

    return {
        'status': True,
        'data': res['data']
    }

if __name__ == "__main__":
    print(process("otp", "query otp { otp_logs { createdDate mobilePhone otpCode } }"))