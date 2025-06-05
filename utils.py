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
    # Split the input string into date and time parts
    date_str, start_time, end_time = datetime_str.split('-')

    # Parse date
    year, month, day = date_str[:4], date_str[4:6], date_str[6:8]
    formatted_date = f"{month}/{day}/{year}"

    # Parse times
    start_hour, start_min = start_time[:2], start_time[2:4]
    end_hour, end_min = end_time[:2], end_time[2:4]

    # Convert to 12-hour format with AM/PM
    start_hour = int(start_hour)
    end_hour = int(end_hour)
    start_period = "AM" if start_hour < 12 else "PM"
    end_period = "AM" if end_hour < 12 else "PM"
    start_hour = start_hour % 12 or 12  # Convert 0 or 12 to 12 for 12-hour format
    end_hour = end_hour % 12 or 12
    formatted_start = f"{start_hour}:{start_min} {start_period}"
    formatted_end = f"{end_hour}:{end_min} {end_period}"

    return f"{formatted_date}, {formatted_start} - {formatted_end}"
