import configparser, json, requests
from services import Hasura
from io import BytesIO

config = configparser.ConfigParser()
config.read('configs.ini')
configOTP = config['OTP']

def process(mobilePhone, otpCode):
    apiCode = configOTP['apiCode']
    passcode = configOTP['passcode']
    endpoint = configOTP['endpoint']
    url = f'{endpoint}?apicode={apiCode}&passcode={passcode}&phone={mobilePhone}&var_str={otpCode}'

    if configOTP['activeCall'] == '1' : 
        response = requests.get(url)
        status_code = response.status_code
        res = response.text
    else:
        status_code = 200
        res = "0"

    if status_code != 200:
        return {
            'status': False,
            'message': "Đã có lỗi từ dịch vụ tổng đài"
        }

    query = 'mutation m_otp{insert_otp_logs_one(object:{mobilePhone:"' + mobilePhone + '",otpCode:"' + otpCode + '", dataResponse:"' + res + '"}) { UUID }}'
    responseInsert = Hasura.process("m_otp", query)
    return responseInsert
    
    return {
        'status': True,
        'data': responseInsert['data']['insert_otp_logs_one']
    }