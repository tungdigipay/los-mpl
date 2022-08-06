def validate_date(text):
    import datetime
    try:
        datetime.datetime.strptime(text, '%Y-%m-%d')
    except ValueError:
        return False
    return True