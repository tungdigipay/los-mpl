import sys, requests
from imp import reload
from repositories import FptEsignRepository

# from Tools.scripts.treesync import raw_input

reload(sys)
# sys.setdefaultencoding('utf-8')

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from datetime import time
from typing import re

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from OpenSSL import crypto

from third_party.esign_fpt.Datatypes.MultipleSigningFileData import MultipleSigningFileData
from third_party.esign_fpt._helpers import _parse_pem_key
from third_party.esign_fpt._helpers import _to_bytes
from third_party.esign_fpt._helpers import _b64encode

import base64, configparser
from third_party.esign_fpt.Datatypes import eSignCloudContant as constant
import time
import json
import requests

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['ESIGN-FPT']

URL = config['url']
FUNCTION_PREPAREFILEFORSIGNCLOUD = 'prepareFileForSignCloud'
FUNCTION_PREPARECERTIFICATEFORSIGNCLOUD = 'prepareCertificateForSignCloud'
FUNCTION_AUTHORIZECOUNTERSIGNINGFORSIGNCLOUD = 'authorizeCounterSigningForSignCloud'
FUNCTION_REGENERATEAUTHORIZATIONCODEFORSIGNCLOUD = 'regenerateAuthorizationCodeForSignCloud'

relyingPartyName = config['relyingPartyName']
relyingPartyUser = config['relyingPartyUser']
relyingPartyPassword = config['relyingPartyPassword']
relyingPartySignature = 'WIMf59KYB19T5oUmVXPsLhh8IhwUhQwIqd1tfh/Ld96rRcbWo/RqoeXL1ZPMJMeNwSyw0737lzIZU+Bs21U0vx498ViJHQzLydr//4HzmoONbObFAc+0ExakIEavKVsWpO5Dy9h0V2m14hqmIT3VHcf4TCWqnXnRaHziNDfJiWKYU2xq27RUP+t2WOti+8Simyv1VGHY6/DSZ/PddI34pQ3Vb9UZmBt/mCAL2O2EP5D8cQ2CQz9fs4ZCy1A0qurZpV3mEgt/dfpKSYDt+VvTcyVGZndVAlFP54GyOPp3LESMui+AaxAeElQFF9vnReCmJEgv7UCwu48gQya/OOvOVw=='
relyingPartyKeyStore = 'third_party/esign_fpt/DIGIPAY_DEMO.p12'
relyingPartyKeyStorePassword = config['relyingPartyKeyStorePassword']
certificateProfile = 'PERS.1D'

# Constant
c = constant.eSignCloudContant()

# current timestamp
currenttimemillis = lambda: int(round(time.time() * 1000))


def prepareCertificateForSignCloud(agreementUUID, data):
    personalid = data['idNumber']
    personalname = data['customerName']
    location = data['address']
    stateprovince = data['city']
    country = 'VN'
    certificateprofile = 'PERS.1D'
    authorizationemail = data['customerEmail']
    authorizationmobileno = data['customerPhone']
    imgfront = _b64encode(requests.get(data['idNumberFrontImage']).content)
    # print(imgfront)
    imgback = _b64encode(requests.get(data['idNumberBackImage']).content)

    timestamp = str(currenttimemillis())
    datatobesign = relyingPartyUser + relyingPartyPassword + relyingPartySignature + timestamp
    pkcs1signature = generatePKCS1Signature(datatobesign)

    # create JSON call server
    payload = "{"
    payload += "   \"relyingParty\":\"" + relyingPartyName + "\","
    payload += "   \"agreementUUID\":\"" + agreementUUID + "\","
    payload += "   \"mobileNo\":\"" + authorizationmobileno + "\","
    payload += "   \"email\":\"" + authorizationemail + "\","
    payload += "   \"certificateProfile\":\"" + certificateProfile + "\","
    payload += "   \"agreementDetails\":{"
    payload += "      \"personalName\":\"" + personalname + "\","
    payload += "      \"location\":\"" + location + "\","
    payload += "      \"stateOrProvince\":\"" + stateprovince + "\","
    payload += "      \"country\":\"" + country + "\","
    payload += "      \"personalID\":\"" + personalid + "\","
    payload += "      \"photoFrontSideIDCard\":\"" + imgfront.decode('utf-8') + "\","
    payload += "      \"photoBackSideIDCard\":\"" + imgback.decode('utf-8') + "\""
    payload += "   },"
    payload += "   \"credentialData\":{"
    payload += "      \"username\":\"" + relyingPartyUser + "\","
    payload += "      \"password\":\"" + relyingPartyPassword + "\","
    payload += "      \"signature\":\"" + relyingPartySignature + "\","
    payload += "      \"pkcs1Signature\":\"" + pkcs1signature.decode('utf-8') + "\","
    payload += "      \"timestamp\":\"" + timestamp + "\""
    payload += "   }"
    payload += "}"

    payload = payload.encode('utf-8')
    # print('payload: '+payload)

    response = requests.post(URL + FUNCTION_PREPARECERTIFICATEFORSIGNCLOUD, data=payload)
    # print('Response: ' + response.text)
    signcloudresp = json.loads(response.text)

    FptEsignRepository.storage(data['applicationID'], {
        "payload": json.dumps(data),
        "response": response.text
    })

    if signcloudresp['responseCode'] == 0 or signcloudresp['responseCode'] == 1010:
        return {
            "status": True,
            "data": signcloudresp
        }
    else:
        return {
            "status": False,
            "message": signcloudresp['responseMessage']
        }
        print(signcloudresp['responseCode'])
        print(signcloudresp['responseMessage'])

def prepareFileForSignCloud(agreementUUID, data):
    timestamp = str(currenttimemillis())
    datatobesign = relyingPartyUser + relyingPartyPassword + relyingPartySignature + timestamp
    pkcs1Signature = generatePKCS1Signature(datatobesign)

    authorizeMethod = str(c.AUTHORISATION_METHOD_SMS)
    signingFileData = _b64encode(requests.get(data['contractFile']).content)
    signingFileName = data['contractFileName']
    mimetype = c.MIMETYPE_PDF
    smsMessage = 'Ma xac thuc (OTP) de ky Hop dong Dien Tu cua Quy khach la: {AuthorizeCode}. Chu y khong cung cap ma OTP nay cho bat ky ai.'
    messagingmode = str(c.ASYNCHRONOUS_CLIENTSERVER)

    payload = "{"
    payload += "   \"relyingParty\":\"" + relyingPartyName + "\","
    payload += "   \"agreementUUID\":\"" + agreementUUID + "\","
    payload += "   \"credentialData\":{"
    payload += "      \"username\":\"" + relyingPartyUser + "\","
    payload += "      \"password\":\"" + relyingPartyKeyStorePassword + "\","
    payload += "      \"signature\":\"" + relyingPartySignature + "\","
    payload += "      \"pkcs1Signature\":\"" + \
               (pkcs1Signature).decode('utf-8') + "\","
    payload += "      \"timestamp\":\"" + timestamp + "\""
    payload += "   },"
    payload += "   \"signingFileData\":\"" + \
               (signingFileData).decode('utf-8') + "\","
    payload += "   \"signingFileName\":\"" + signingFileName + "\","
    payload += "   \"mimeType\":\"" + mimetype + "\","
    payload += "   \"notificationTemplate\":\"" + smsMessage + "\","
    payload += "   \"notificationTemplate\":\"" + smsMessage + "\","
    payload += "   \"authorizeMethod\":" + messagingmode + ","
    payload += "   \"signCloudMetaData\":{"
    payload += "      \"singletonSigning\":{"
    payload += "         \"COUNTERSIGNENABLED\":\"True\","
    payload += "         \"PAGENO\":\"1\","
    payload += "         \"POSITIONIDENTIFIER\":\"CHỮ KÝ KHÁCH HÀNG\","
    payload += "         \"RECTANGLEOFFSET\":\"-30,-100\","
    payload += "         \"RECTANGLESIZE\":\"210,80\","
    payload += "         \"VISIBLESIGNATURE\":\"True\","
    payload += "         \"VISUALSTATUS\":\"False\","
    payload += "         \"SHOWSIGNERINFO\":\"True\","
    payload += "         \"SIGNERINFOPREFIX\":\"Ký bởi:\","
    payload += "         \"SHOWREASON\":\"True\","
    payload += "         \"SIGNREASONPREFIX\":\"Lý do:\","
    payload += "         \"SIGNREASON\":\"Tôi đồng ý\","
    payload += "         \"SHOWDATETIME\":\"True\","
    payload += "         \"DATETIMEPREFIX\":\"Ký ngày:\","
    payload += "         \"SHOWLOCATION\":\"True\","
    payload += "         \"LOCATIONPREFIX\":\"Nơi ký:\","
    payload += "         \"LOCATION\":\"Hà Nội\","
    payload += "         \"TEXTDIRECTION\":\"LEFTTORIGHT\","
    payload += "         \"TEXTCOLOR\":\"black\""
    payload += "      },"
    payload += "      \"counterSigning\":{"
    payload += "         \"PAGENO\":\"1\","
    payload += "         \"POSITIONIDENTIFIER\":\"CHỮ KÝ DOANH NGHIỆP\","
    payload += "         \"RECTANGLEOFFSET\":\"-30,-100\","
    payload += "         \"RECTANGLESIZE\":\"210,80\","
    payload += "         \"VISIBLESIGNATURE\":\"True\","
    payload += "         \"VISUALSTATUS\":\"False\","
    payload += "         \"SHOWSIGNERINFO\":\"True\","
    payload += "         \"SIGNERINFOPREFIX\":\"Ký bởi:\","
    payload += "         \"SHOWREASON\":\"True\","
    payload += "         \"SIGNREASONPREFIX\":\"Lý do:\","
    payload += "         \"SIGNREASON\":\"Tôi đồng ý\","
    payload += "         \"SHOWDATETIME\":\"True\","
    payload += "         \"DATETIMEPREFIX\":\"Ký ngày:\","
    payload += "         \"SHOWLOCATION\":\"True\","
    payload += "         \"LOCATIONPREFIX\":\"Nơi ký:\","
    payload += "         \"LOCATION\":\"Hà Nội\","
    payload += "         \"TEXTDIRECTION\":\"LEFTTORIGHT\","
    payload += "         \"TEXTCOLOR\":\"black\""
    payload += "      }"
    payload += "   }"
    payload += "}"

    payload = payload.encode('utf-8')
    response = requests.post(URL + FUNCTION_PREPAREFILEFORSIGNCLOUD, data=payload)
    signcloudresp = json.loads(response.text)
    
    FptEsignRepository.storage(data['applicationID'], {
        "payload": json.dumps(data),
        "response": response.text,
        "otpCode": signcloudresp['authorizeCredential'],
        "agreementUUID": agreementUUID,
        "billCode": signcloudresp['billCode']
    })

    if signcloudresp['responseCode'] == 1007:
        # print(signcloudresp['responseMessage'])
        # print('BillCode:' + signcloudresp['billCode'])
        return {
            "status": True,
            "data": signcloudresp
        }
    else:
        return {
            "status": False,
            "message": signcloudresp['responseMessage']
        }
        # print(signcloudresp['responseCode'])
        # print(signcloudresp['responseMessage'])

def authorizeCounterSigningForSignCloud(agreementUUID, otpCode, BillCode):
    authorizecode = otpCode
    billcode = BillCode
    messagingmode = str(c.SYNCHRONOUS)

    timestamp = str(currenttimemillis())
    datatobesign = relyingPartyUser + relyingPartyPassword + relyingPartySignature + timestamp
    pkcs1signature = generatePKCS1Signature(datatobesign)

    payload = "{"
    payload += "  \"relyingParty\": \"" + relyingPartyName + "\","
    payload += "  \"agreementUUID\": \"" + agreementUUID + "\","
    payload += "  \"credentialData\": {"
    payload += "    \"username\": \"" + relyingPartyUser + "\","
    payload += "    \"password\": \"" + relyingPartyKeyStorePassword + "\","
    payload += "    \"signature\": \"" + relyingPartySignature + "\","
    payload += "    \"pkcs1Signature\": \"" + pkcs1signature.decode('utf-8') + "\","
    payload += "    \"timestamp\": \"" + timestamp + "\""
    payload += "  },"
    payload += "  \"authorizeCode\": \"" + authorizecode + "\","
    payload += "  \"billCode\": \"" + billcode + "\","
    payload += "  \"messagingMode\": " + messagingmode + " "
    payload += "}"

    response = requests.post(URL + FUNCTION_AUTHORIZECOUNTERSIGNINGFORSIGNCLOUD, data=payload)  # verify=True
    # print('Response: ' + response.text)
    signcloudresp = json.loads(response.text)

    if signcloudresp['responseCode'] == 0:
        # print(signcloudresp['responseMessage'])
        # print(signcloudresp['billCode'])

        # write to file
        signedfiledata = open("files/esign/sample.signed.pdf", "wb")
        base64_bytes = signcloudresp['signedFileData'].encode('utf-8')
        signedfiledata.write(base64.standard_b64decode(base64_bytes))
        # print('Signed File is saved successfully')
        signedfiledata.close()
        return {
            "status": True,
            "data": signcloudresp
        }
    else:
        # print(signcloudresp['responseCode'])
        # print(signcloudresp['responseMessage'])
        return {
            "status": False,
            "message": signcloudresp['responseMessage']
        }


def regenerateAuthorizationCodeForSignCloud(agreementUUID):
    timestamp = str(currenttimemillis())
    datatobesign = relyingPartyUser + relyingPartyPassword + relyingPartySignature + timestamp
    pkcs1signature = generatePKCS1Signature(datatobesign)
    smsmessage = 'Ma xac thuc (OTP) de ky Hop dong Dien Tu cua Quy khach la: {AuthorizeCode}. Chu y khong cung cap ma OTP nay cho bat ky ai.'
    authorizemethod = str(c.AUTHORISATION_METHOD_SMS)

    payload = "{"
    payload += "   \"relyingParty\":\"" + relyingPartyName + "\","
    payload += "   \"agreementUUID\":\"" + agreementUUID + "\","
    payload += "   \"credentialData\":{"
    payload += "      \"username\":\"" + relyingPartyUser + "\","
    payload += "      \"password\":\"" + relyingPartyKeyStorePassword + "\","
    payload += "      \"signature\":\"" + relyingPartySignature + "\","
    payload += "      \"pkcs1Signature\":\"" + pkcs1signature.decode('utf-8') + "\","
    payload += "      \"timestamp\":\"" + timestamp + "\""
    payload += "   },"
    payload += "   \"notificationTemplate\":\"" + smsmessage + "\","
    payload += "   \"authorizeMethod\":" + authorizemethod
    payload += "}"

    response = requests.post(URL + FUNCTION_REGENERATEAUTHORIZATIONCODEFORSIGNCLOUD, data=payload)
    # print('Response: ' + response.text)
    signcloudresp = json.loads(response.text)
    if signcloudresp['responseCode'] == 1007:
        # print(signcloudresp['responseMessage'])
        # print(signcloudresp['billCode'])
        return {
            "status": True,
            "data": signcloudresp
        }
    else:
        # print(signcloudresp['responseCode'])
        # print(signcloudresp['responseMessage'])
        return {
            "status": False,
            "message": signcloudresp['responseMessage']
        }


def generatePKCS1Signature(data):
    p12 = crypto.load_pkcs12(open(relyingPartyKeyStore, 'rb').read(), relyingPartyKeyStorePassword)
    pkeypem = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
    parsed_pem_key = _parse_pem_key(_to_bytes(pkeypem))
    key = RSA.importKey(parsed_pem_key)
    h = SHA.new(data.encode(encoding='UTF-8', errors='strict'))
    signer = PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    return _b64encode(signature)
