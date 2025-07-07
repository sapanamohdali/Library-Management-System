from datetime import datetime

def calculate_late_fee(issue_date, return_date, per_day_fee=2):
    fmt = "%Y-%m-%d"
    days = (datetime.strptime(return_date, fmt) - datetime.strptime(issue_date, fmt)).days
    if days <= 14:
        return 0
    return (days - 14) * per_day_fee
