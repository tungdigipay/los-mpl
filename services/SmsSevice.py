from libraries import Sms

def approve(mobilePhone, contractNumber, link):
    sms_out = f"Mfast Pay Later da phe duyet ho so vay {contractNumber}. Vui long truy cap {link} de xem va ky hop dong dien tu."
    return __process(mobilePhone, sms_out)

def reject(mobilePhone):
    sms_out = f"Rat tiec, hien tai chua co khoan vay nao phu hop cho Quy khach. Mong Quy khach thong cam va vui long lien he lai sau."
    return __process(mobilePhone, sms_out)

def delivery(mobilePhone, brandName, eVoucher):
    sms_out = f"Ma su dung {brandName} cua QK là: {eVoucher}. Tran trong."
    return __process(mobilePhone, sms_out)

def __process(mobilePhone, sms_out):
    return Sms.process(mobilePhone, sms_out)