from repositories import OtpRepository, EsignRepository
from services import SmsSevice
from libraries import Hasura, S3
import random, string

def preparing(application):
    contract_number = __gen_contract_number(application)

    note = "Đã sinh hợp đồng và chờ khách hàng ký"
    esignPwd = __create_pwd()
    res = __update_application(application, {
        "statusID": 14,
        "note": note,
        "contractNumber": contract_number
    })
    application = res['data']['update_LOS_applications_by_pk']

    contractFile = __contract_file(application, contract_number)
    EsignRepository.storage(application, {
        'esignPwd': esignPwd,
        "contractFile": contractFile
    })

    __send_sms(application, contract_number, esignPwd)
    return {
        "status": True,
        "message": "Đã sinh hợp đồng và chờ khách hàng ký"
    }

def verify(request):
    res = EsignRepository.verify_application(request.contractNumber, request.idNumber, request.password)
    return res

def otp(request):
    return OtpRepository.record_log(request.mobilePhone, request.otpCode, "successful")

def process(request):
    return {
        "status": True,
        "message": "Thành công"
    }

def __gen_contract_number(application):
    from datetime import date
    today = date.today()

    applicationID = application['ID']
    applicationID_text = str(applicationID)
    if applicationID > 10000: applicationID_text = applicationID_text[-4:len(applicationID_text)]
    else: applicationID_text = applicationID_text.zfill(4)

    contract_number = "11" + today.strftime("%y%m%d") + applicationID_text
    return contract_number

def __update_application(application, data):
    appID = application['ID']
    objects = create_objects(data)
    query = """
    mutation m_update_LOS_applications_by_pk {
        update_LOS_applications_by_pk(
            pk_columns: { ID: %d }, 
            _set: { %s }
        ) {
            ID
            LOS_customer {
                fullName
                LOS_master_gender {
                    label
                }
                dateOfBirth
                idNumber
            }
            LOS_customer_profile {
                idNumber_dateOfIssue
                idNumber_issuePlace
                mobilePhone
                LOS_master_marital_status {
                    label
                }
                permanentAddressDetail
                permanent_LOS_master_location_ward {
                    name
                }
                permanent_LOS_master_location_district {
                    name
                }
                permanent_LOS_master_location_province {
                    name
                }
            }
            loanTenor
            loanAmount
        }
    }
    """ % (appID, objects)

    res = Hasura.process("m_update_LOS_applications_by_pk", query)
    return res

def create_objects(data) -> str:
    objects = ""
    if 'statusID' in data:
        objects += "statusID: %d, " % (data['statusID'])
    if 'note' in data:
        objects += 'note: "%s", ' % (data['note'])
    if 'contractNumber' in data:
        objects += 'contractNumber: "%s", ' % (data['contractNumber'])

    return objects

def __send_sms(application, contract_number, esignPwd):
    mobilePhone = application['LOS_customer_profile']['mobilePhone']
    link = "https://1ljz.short.gy/I6sAqn"
    SmsSevice.approve(mobilePhone, contract_number, link, esignPwd)

def __create_pwd() -> str:
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))

def __contract_file(application, contract_number):
    # return "https://s3-sgn09.fptcloud.com/appay.cloudcms/contract_template.pdf"
    from libraries import CreatePDF
    from helpers import CommonHelper

    LOS_customer_profile = application['LOS_customer_profile']
    loanAmount = application['loanAmount']
    fullName = application['LOS_customer']['fullName']
    gender = application['LOS_customer']['LOS_master_gender']['label']
    dateOfBirth = application['LOS_customer']['dateOfBirth']
    idNumber = application['LOS_customer']['idNumber']
    idNumber_dateOfIssue = LOS_customer_profile['idNumber_dateOfIssue']
    idNumber_issuePlace = LOS_customer_profile['idNumber_issuePlace']
    marital = "" if LOS_customer_profile['LOS_master_marital_status'] == None else LOS_customer_profile['LOS_master_marital_status']['label']
    
    if LOS_customer_profile['permanentAddressDetail'] == None:
        address = ""
    else:
        address = LOS_customer_profile['permanentAddressDetail'] + ", "
    address += LOS_customer_profile['permanent_LOS_master_location_ward']['name'] + ", "
    address += LOS_customer_profile['permanent_LOS_master_location_district']['name'] + ", "
    address += LOS_customer_profile['permanent_LOS_master_location_province']['name']

    if idNumber_issuePlace == "CỤC TRƯỞNG CỤC CẢNH SÁT QUẢN LÝ HÀNH CHÍNH VỀ TRẬT TỰ XÃ HỘI":
        idNumber_issuePlace = "CTCCSQLHCVTTXH"

    ins_amount = int(loanAmount * 5/ 100)

    data = {
        0: [
            [244, 762, "02"],
            [310, 762, "08"],
            [373, 762, "22"],
            [210, 455, fullName],
        ],
        1: [
            [180, 683, fullName],
            [180, 666, gender],
            [420, 666, dateOfBirth],

            [180, 648, idNumber],
            [420, 648, idNumber_dateOfIssue],

            [180, 630, idNumber_issuePlace],
            [420, 630, marital],

            [180, 613, address],

            [65, 310, "TRA GOP VOUCHER GOTIT 0%"],
        ],
        2: [
            [195, 290, '{0:,}'.format(loanAmount)],
            [195, 269, CommonHelper.number_to_text(loanAmount)],
            [295, 249, '{0:,}'.format(ins_amount)],
        ],
        11: [
            [137, 505, fullName],
        ]
    }

    template = "files/esign/contract_template.pdf"
    output = f"files/esign/contract_{contract_number}.pdf"
    contract = CreatePDF.gen(template, output, data)
    return S3.upload(contract, f"contract_{contract_number}.pdf")