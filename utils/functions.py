from datetime import datetime
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import random
import time


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
    return agents[random.randint(0, len(agents) - 1)]


def find_element_by_css(driver: webdriver.Chrome, selector: str) -> WebElement:
    return driver.find_element(By.CSS_SELECTOR, selector)


def find_element_text(driver: webdriver.Chrome, selector: str) -> str:
    return find_element_by_css(driver, selector).text.strip()


def click_element(driver: webdriver.Chrome, selector: str) -> None:
    find_element_by_css(driver, selector).click()
    time.sleep(0.25)
