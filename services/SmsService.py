from libraries import Sms

def approve(mobilePhone, contractNumber, link, esignPwd):
    sms_out = f"Mfast Pay Later da phe duyet ho so vay {contractNumber} và mat khau {esignPwd}. Vui long truy cap {link} de xem va ky hop dong dien tu."
    return __process(mobilePhone, sms_out)

def reject(mobilePhone):
    sms_out = f"Rat tiec, hien tai MFast khong co khoan tra cham nao phu hop voi nhu cau cua Quy khach. Chan thanh cam on !"
    return __process(mobilePhone, sms_out)

def cancel(mobilePhone):
    sms_out = "Rat tiec, chua co ho so tra cham phu hop voi de nghi cua Quy khach. Vui long lien he Nhan vien tu van de duoc ho tro. Xin cam on !"
    return __process(mobilePhone, sms_out)

def delivery(mobilePhone, brandName, eVoucher):
    sms_out = f"Ma su dung {brandName} cua QK là: {eVoucher}. Tran trong."
    return __process(mobilePhone, sms_out)

def esign(mobilePhone, sms_out):
    return __process(mobilePhone, sms_out)

def activition(mobilePhone, sms_out):
    return __process(mobilePhone, sms_out)

def __process(mobilePhone, sms_out):
    return Sms.process(mobilePhone, sms_out)