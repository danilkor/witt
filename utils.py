from datetime import datetime, timedelta
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

# Example
# datetime_str = "20250602-1400-1450"
def format_datetime_range(datetime_str):
    date_str, start_time, end_time = datetime_str.split('-')
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    start_time_obj = datetime.strptime(start_time, "%H%M")
    end_time_obj = datetime.strptime(end_time, "%H%M")
    formatted_date = date_obj.strftime("%B %d, %Y")
    formatted_start = start_time_obj.strftime("%I:%M %p")
    formatted_end = end_time_obj.strftime("%I:%M %p")
    day_of_week = date_obj.strftime("%A")
    return f"{formatted_date}, {formatted_start} - {formatted_end} == {day_of_week}"


def validate_date(date_str):
    """
    Validate if date_str is in YYYYMMDD format and represents a valid date.

    Args:
        date_str (str): Date string to validate (e.g., '20250602')

    Returns:
        bool: True if valid, False otherwise
    """
    # Check if string is 8 digits
    if not (isinstance(date_str, str) and len(date_str) == 8 and date_str.isdigit()):
        return False

    try:
        # Parse year, month, day
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])

        # Basic range checks
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
        if not (1000 <= year <= 9999):  # Reasonable year range
            return False

        # Validate date using datetime
        from datetime import datetime
        datetime(year, month, day)
        return True
    except ValueError:
        # Invalid date (e.g., Feb 30, April 31)
        return False


def get_week_range(date_str):
    # Parse input date
    date_obj = datetime.strptime(date_str, "%Y%m%d")

    # Find Monday (start of week)
    start_of_week = date_obj - timedelta(days=date_obj.weekday())

    # Find Sunday (end of week)
    end_of_week = start_of_week + timedelta(days=4)

    # Format dates
    start_formatted = start_of_week.strftime("%d. %B %Y").lstrip("0")
    end_formatted = end_of_week.strftime("%d. %B %Y").lstrip("0")

    return f"{start_formatted} - {end_formatted}"


def is_time_in_lesson_range(start_time, end_time):
    # Get current time in CEST
    current_time = datetime.now()

    # Convert current time to minutes since midnight
    current_time_minutes = current_time.hour * 60 + current_time.minute

    # Convert start and end times to minutes since midnight
    start_hour = start_time // 100
    start_minute = start_time % 100
    end_hour = end_time // 100
    end_minute = end_time % 100

    start_minutes = start_hour * 60 + start_minute
    end_minutes = end_hour * 60 + end_minute

    # Check if current time is within the lesson time range
    return start_minutes <= current_time_minutes <= end_minutes
