from datetime import datetime

def calculate_remaining_days(expire_time):
    expire_date = datetime.strptime(expire_time.split('T')[0], '%Y-%m-%d')
    remaining_days = (expire_date - datetime.now()).days
    return remaining_days 