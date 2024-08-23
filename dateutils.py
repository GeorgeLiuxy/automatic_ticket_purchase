from datetime import datetime, timedelta

def get_next_weekday_date(weekday):
    """
    根据当前日期，获取下周指定的星期几的日期
    :param weekday: 目标星期几，0=周一, 1=周二, ..., 6=周日
    :return: 下周目标日期的字符串，格式为 'YYYY-MM-DD'
    """
    today = datetime.today()
    days_ahead = weekday - today.weekday() + 7
    if days_ahead <= 0:
        days_ahead += 7
    next_weekday = today + timedelta(days=days_ahead)
    return next_weekday.strftime("%Y-%m-%d")

if __name__ == "__main__":
    # 假设今天是2024-08-22（星期四），我们需要获取下周四的日期
    next_thursday = get_next_weekday_date(8)  # 3代表星期四
    print(f"下周四的日期是: {next_thursday}")
