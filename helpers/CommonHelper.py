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

def calc_emi(amount, tenor, interest_rate):
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