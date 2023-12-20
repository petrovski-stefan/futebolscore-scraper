from datetime import datetime
from selenium.webdriver.remote.webelement import WebElement
import random


def calculate_days_difference(last_game_date: str, date_time: str) -> int:

    last_game_date_parsed = datetime.strptime(last_game_date, "%d-%m %Y")

    date_time_parts = date_time.split(" ")
    date_time_parsed = datetime.strptime(date_time_parts[0], "%d-%m-%Y")

    difference = (date_time_parsed - last_game_date_parsed).days

    return difference


def get_team_next_game_location(web_element: WebElement) -> str:
    if web_element.get_attribute("class") == "b":
        return "Home"
    elif web_element != "":
        return "Away"

    return ""


def get_team_last_game_location(web_element: WebElement, team_name: str) -> str:
    extracted_team_name = web_element.text.strip()

    if team_name == "":
        return ""

    if extracted_team_name == team_name:
        return "Home"
    return "Away"


def get_random_agent(agents: list[str]) -> str:
    return agents[random.randint(0, len(agents)-1)]
