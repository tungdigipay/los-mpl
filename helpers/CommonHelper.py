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