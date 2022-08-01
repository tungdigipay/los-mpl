import pycurl, configparser, json
from services import Hasura
from io import BytesIO

config = configparser.ConfigParser()
config.read('configs.ini')
configOTP = config['OTP']

def process(mobilePhone, otpCode):
    data_response = BytesIO()
    apiCode = configOTP['apiCode']
    passcode = configOTP['passcode']
    endpoint = configOTP['endpoint']
    url = f'{endpoint}?apicode={apiCode}&passcode={passcode}&phone={mobilePhone}&var_str={otpCode}'

    c = pycurl.Curl()
    c.setopt(c.URL, url)

    if configOTP['activeCall'] == '1' : 
        c.perform()
        c.setopt(c.WRITEDATA, data_response)
        status_code = c.getinfo(c.RESPONSE_CODE)
        get_body = data_response.getvalue()
        res = json.loads(get_body.decode('utf8'))
    else:
        status_code = 200
        res = "0"

    c.close()

    if status_code != 200:
        return {
            'status': False,
            'message': "Đã có lỗi từ dịch vụ tổng đài"
        }

    query = 'mutation m_otp{insert_otp_logs_one(object:{mobilePhone:"' + mobilePhone + '",otpCode:"' + otpCode + '", dataResponse:"' + res + '"}) { UUID }}'
    responseInsert = Hasura.process("m_otp", query)
    
    return {
        'status': True,
        'data': responseInsert['data']['insert_otp_logs_one']
    }