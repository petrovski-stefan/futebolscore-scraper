from datetime import datetime


def calculate_days_difference(last_game_date: str, date_time: str) -> int:

    last_game_date_parsed = datetime.strptime(last_game_date, "%d-%m %Y")

    date_time_parts = date_time.split(" ")
    date_time_parsed = datetime.strptime(date_time_parts[0], "%d-%m-%Y")

    difference = (date_time_parsed - last_game_date_parsed).days

    return difference
