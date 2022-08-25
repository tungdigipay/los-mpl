def validate_date(text):
    import datetime
    try:
        datetime.datetime.strptime(text, '%Y-%m-%d')
    except ValueError:
        return False
    return True

def is_json(text):
    import json
    try:
        json.loads(text)
    except ValueError as e:
        return False
    return True

def is_uuid(text):
    from uuid import UUID
    try:
        return UUID(text).version
    except ValueError:
        return False

def get_age(dateOfBirth):
    from datetime import date

    birthdate_split = dateOfBirth.split("-")
    birthdate = date(int(birthdate_split[0]), int(birthdate_split[1]), int(birthdate_split[2]))
    
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def calc_emi(amount, tenor, interest_rate=0):
    P = amount
    I = 0
    t = tenor
    n = tenor/ 12

    emi = (P + I) / (t * n)
    return round(emi)

def list_status_for_processing():
    return [3, 6, 7, 10, 13, 14, 15, 18, 19, 20, 21, 22]

def list_status_for_refused():
    return [4, 5, 8, 9, 11, 12, 16, 17, 24]

def list_status_for_rejected():
    return [5, 9, 11, 17]

def thirty_days_ago():
    from datetime import datetime, timedelta
    today = datetime. today()
    return today - timedelta(days=30)

def is_email(email):
    import re
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return True if re.fullmatch(regex, email) else False

def number_to_text(num):
    d = { 0 : 'không', 1 : 'một', 2 : 'hai', 3 : 'ba', 4 : 'bốn', 5 : 'năm',
          6 : 'sáu', 7 : 'bảy', 8 : 'tám', 9 : 'chín', 10 : 'mười',
          11 : 'mười một', 12 : 'mười hai', 13 : 'mười ba', 14 : 'mười bốn',
          15 : 'mười lăm', 16 : 'mười sáu', 17 : 'mười bảy', 18 : 'mười tám',
          19 : 'mười chín', 20 : 'hai mươi',
          30 : 'ba mươi', 40 : 'bốn mươi', 50 : 'năm mươi', 60 : 'sáu mươi',
          70 : 'bảy mươi', 80 : 'tám mươi', 90 : 'chín mươi' }
    k = 1000
    m = k * 1000
    b = m * 1000
    t = b * 1000

    assert(0 <= num)

    if (num < 20):
        return d[num]

    if (num < 100):
        if num % 10 == 0: return d[num]
        else: return d[num // 10 * 10] + '-' + d[num % 10]

    if (num < k):
        if num % 100 == 0: return d[num // 100] + ' trăm đồng'
        else: return d[num // 100] + ' trăm ' + number_to_text(num % 100) + " đồng"

    if (num < m):
        if num % k == 0: return number_to_text(num // k) + ' ngàn' + " đồng"
        else: return number_to_text(num // k) + ' ngàn, ' + number_to_text(num % k) + " đồng"

    if (num < b):
        if (num % m) == 0: return number_to_text(num // m) + ' triệu' + " đồng"
        else: return number_to_text(num // m) + ' triệu, ' + number_to_text(num % m) + " đồng"

    if (num < t):
        if (num % b) == 0: return number_to_text(num // b) + ' tỷ' + " đồng"
        else: return number_to_text(num // b) + ' tỷ, ' + number_to_text(num % b) + " đồng"

    raise AssertionError('num is too large: %s' % str(num))