from datetime import date

def arabic_pluralize(singular, plural, count):
    if count < 0:
        raise Exception("Count must be less than zero!")
    elif count == 0:
        return ""
    elif count == 1:
        return singular
    else:
        return f"{count} {plural}"
    
def add_if_errors(always_str, error_str, field, extra_or=False):
    if field.errors or extra_or:
        return always_str + " " + error_str        
    return always_str

def readable_date(dt: date):
    return dt.strftime('%Y/%m/%d')

def remaining_days_ceil(dt):
    now = date.today()
    timedelta = dt - now
    
    if timedelta.days == 0:
        return ''
    
    return timedelta.days