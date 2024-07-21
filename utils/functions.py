from datetime import datetime
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import random
import time
import re
from datetime import timedelta, date
import requests
from bs4 import BeautifulSoup, Tag
import os
from selectors.fixtures_selectors import *


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


def click_date(driver: webdriver.Chrome, is_for_today: bool) -> None:
    predictions_date = date.today()
    if not is_for_today:
        predictions_date += timedelta(1)
    predictions_date_selector = (
        f".da_{predictions_date.year}-{predictions_date.month}-{predictions_date.day}"
    )

    date_section = driver.find_element(By.CSS_SELECTOR, dates_wrapper)

    predictions_date_button_text = (
        f"0{predictions_date.day}"
        if predictions_date.day < 10
        else f"{predictions_date.day}"
    )

    prediction_date_button_text_by_regex = re.findall(
        r"\d\d",
        date_section.find_element(By.CSS_SELECTOR, predictions_date_selector).text,
    )[0]

    if prediction_date_button_text_by_regex == predictions_date_button_text:
        predictions_date_button = date_section.find_element(
            By.CSS_SELECTOR, predictions_date_selector
        )
        if predictions_date_button is not None:
            predictions_date_button.click()

    time.sleep(2)


def click_sort_by_time(driver: webdriver.Chrome) -> None:
    filterby_element = driver.find_element(By.CSS_SELECTOR, filterby_element_selector)

    if filterby_element.text.strip() == "Por Liga":
        filterby_element.click()
        time.sleep(3)


def click_show_all(driver: webdriver.Chrome) -> None:
    driver.find_element(By.CSS_SELECTOR, show_all_btn).click()
    time.sleep(2)


def click_tz(driver: webdriver.Chrome) -> None:
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#chooseTimeZone").click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "#timeZone_2").click()
    time.sleep(2)


def get_last5_str(scores: list[tuple], is_home: bool) -> str:
    if is_home:
        return ",".join(reversed([s[0] for s in scores]))

    return ",".join(reversed([s[1] for s in scores]))


def get_matches_divs(bs: BeautifulSoup, selector: str) -> list[Tag]:
    matches_divs = bs.select(selector)

    return matches_divs[:5]


def get_scores(matches_divs: list[Tag]) -> list[tuple]:
    scores = []
    for match in matches_divs:
        score_spans = match.select(score_spans_selector)
        scores.append(tuple([s.text for s in score_spans]))

    return scores


def get_match_stats(url: str, driver: webdriver.Chrome) -> tuple[str, str]:

    driver.get(url)
    click_element(driver, button_selector)
    html = driver.page_source
    bs = BeautifulSoup(html, "html.parser")
    home_matches_divs = get_matches_divs(bs, home_matches_divs_selector)
    away_matches_divs = get_matches_divs(bs, away_matches_divs_selector)
    home_scores = get_scores(home_matches_divs)
    away_scores = get_scores(away_matches_divs)

    home_last5_str = get_last5_str(home_scores, True)
    away_last5_str = get_last5_str(away_scores, False)

    return home_last5_str, away_last5_str


def get_ai_website_session() -> dict:
    from .driver import config_driver

    url = os.getenv("AI_LOGIN_URL")
    if url is None:
        return {}
    driver = config_driver()
    driver.get(url)
    time.sleep(2)
    driver.find_element(
        By.CSS_SELECTOR,
        "body > div > div.container-fluid > div > div > div > form > button",
    ).click()

    time.sleep(2)
    driver.get(url)
    cookie_val = driver.get_cookie(name="PHPSESSID")
    driver.quit()
    return {"PHPSESSID": cookie_val["value"] if cookie_val is not None else None}


def make_prediction(home_last5: str, away_last5: str, url: str, cookie: dict) -> str:
    body = [("home", home_last5), ("away", away_last5)]
    user_agent = os.getenv("USER_AGENT")
    headers = {"User-Agent": user_agent}
    r = requests.post(url, body, headers=headers, cookies=cookie)
    print(r.text)

    match = re.search(r"\d - \d", r.text)

    pred_score = match.group() if match is not None else ""

    return pred_score.replace("-", ":")
