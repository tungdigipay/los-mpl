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
