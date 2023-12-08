from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import random
import pandas as pd
from selectors.first_team_current_form_selectors import *
from selectors.second_team_current_form_selectors import *
from selectors.general_info_selectors import *
from selectors.first_team_current_form_selectors import *
from selectors.next_game_info_selectors import *
from selectors.odd_even_stats_selectors import *
from selectors.head2head_selectors import *


agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
]


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    agent = agents[random.randint(0, len(agents)-1)]
    chrome_options.add_argument(f"--user-agent={agent}")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    # driver.set_page_load_timeout(15)

    return driver


def get_url(starter_url: str, id: int) -> str:
    return f"{starter_url}{id}"


def get_data(url: str) -> dict:
    driver = config_driver()
    driver.get(url)

    time.sleep(0.25)

    data = {}

    general_info = get_match_general_info(driver)
    first_team_current_form_stats = get_first_team_current_form_stats(driver)
    second_team_current_form_stats = get_second_team_current_form_stats(driver)
    next_game_info = get_next_game_info(driver)
    odd_even_stats = get_odd_even_stats(driver)
    h2h_stats = get_h2h_stats(driver)

    if general_info == None or first_team_current_form_stats == None or second_team_current_form_stats == None or next_game_info == None or odd_even_stats == None or h2h_stats == None:
        raise Exception(
            "Current match is from extra low league or a female match or scheduled for the future.")

    data.update(general_info)
    data.update(first_team_current_form_stats)
    data.update(second_team_current_form_stats)
    data.update(next_game_info)
    data.update(odd_even_stats)
    data.update(h2h_stats)

    print(len(data.keys()))

    return data


def get_match_general_info(driver: webdriver.Chrome) -> dict | None:
    general_info = {}

    try:
        general_info['first_team_name'] = driver.find_element(
            By.CSS_SELECTOR, first_team_name_selector).text.strip()
        general_info['second_team_name'] = driver.find_element(
            By.CSS_SELECTOR, second_team_name_selector).text.strip()
        general_info['league_name'] = driver.find_element(
            By.CSS_SELECTOR, league_name_selector).text.strip()
        general_info['date_time'] = driver.find_element(
            By.CSS_SELECTOR, date_time_selector).text.strip()

        general_info['first_team_goals_final_score'] = driver.find_element(
            By.CSS_SELECTOR, first_team_goals_scored_selector).text.strip()
        general_info['second_team_goals_final_score'] = driver.find_element(
            By.CSS_SELECTOR, second_team_goals_scored_selector).text.strip()

        general_info['game_state'] = driver.find_element(
            By.CSS_SELECTOR, game_state_selector).text.strip()

        # TODO: handle half times

        return general_info
    except Exception as e:
        print(f"Error locating general info section. Returned None.\n{e}")
        return None


def get_first_team_current_form_stats(driver: webdriver.Chrome) -> dict | None:
    first_team_stats = {}

    try:
        # First team totals

        first_team_stats['first_team_total_goals_scored'] = int(driver.find_element(
            By.CSS_SELECTOR, first_team_total_goals_scored_selector).text.strip())

        first_team_stats['first_team_total_goals_conceded'] = int(driver.find_element(
            By.CSS_SELECTOR, first_team_total_goals_conceded_selector).text.strip())

        first_team_stats['first_team_goals_difference'] = int(driver.find_element(
            By.CSS_SELECTOR, first_team_goals_difference_selector).text.strip())

        first_team_stats['first_team_scoring_average'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_scoring_average_selector).text.strip())

        # First team at home

        first_team_stats['first_team_at_home_total_goals_scored'] = int(driver.find_element(
            By.CSS_SELECTOR, first_team_at_home_total_goals_scored_selector).text.strip())

        first_team_stats['first_team_at_home_total_goals_conceded'] = int(driver.find_element(
            By.CSS_SELECTOR, first_team_at_home_total_goals_conceded_selector).text.strip())

        first_team_stats['first_team_at_home_goals_difference'] = int(driver.find_element(
            By.CSS_SELECTOR, first_team_at_home_goals_difference_selector).text.strip())

        first_team_stats['first_team_at_home_scoring_average'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_at_home_scoring_average_selector).text.strip())
    except NoSuchElementException as e:
        print(
            f"Error locating first team current form section. Returned None.\n{e}")
        return None

    return first_team_stats


def get_second_team_current_form_stats(driver: webdriver.Chrome) -> dict | None:
    second_team_stats = {}

    try:
        # Second team totals

        second_team_stats['second_team_total_goals_scored'] = int(driver.find_element(
            By.CSS_SELECTOR, second_team_total_goals_scored_selector).text.strip())

        second_team_stats['second_team_total_goals_conceded'] = int(driver.find_element(
            By.CSS_SELECTOR, second_team_total_goals_conceded_selector).text.strip())

        second_team_stats['second_team_goals_difference'] = int(driver.find_element(
            By.CSS_SELECTOR, second_team_goals_difference_selector).text.strip())

        second_team_stats['second_team_scoring_average'] = float(driver.find_element(
            By.CSS_SELECTOR, second_team_scoring_average_selector).text.strip())

        # Second team away

        second_team_stats['second_team_away_total_goals_scored'] = int(driver.find_element(
            By.CSS_SELECTOR, second_team_away_total_goals_scored_selector).text.strip())

        second_team_stats['second_team_away_total_goals_conceded'] = int(driver.find_element(
            By.CSS_SELECTOR, second_team_away_total_goals_conceded_selector).text.strip())

        second_team_stats['second_team_away_goals_difference'] = int(driver.find_element(
            By.CSS_SELECTOR, second_team_away_goals_difference_selector).text.strip())

        second_team_stats['second_team_away_scoring_average'] = float(driver.find_element(
            By.CSS_SELECTOR, second_team_away_scoring_average_selector).text.strip())

    except NoSuchElementException as e:
        print(
            "Error locating second team current form stats table. Returned empty dictionary", e)
        return {}

    return second_team_stats


def get_next_game_info(driver: webdriver.Chrome) -> dict | None:
    next_game_info = {}

    try:
        next_game_info['first_team_days_until_next_game'] = driver.find_element(
            By.CSS_SELECTOR, first_team_days_until_next_game_selector).text.strip()
        next_game_info['second_team_days_until_next_game'] = driver.find_element(
            By.CSS_SELECTOR, second_team_days_until_next_game_selector).text.strip()
        next_game_info['first_team_next_game_location'] = driver.find_element(
            By.CSS_SELECTOR, first_team_next_game_location_selector).text.strip()
        next_game_info['second_team_next_game_location'] = driver.find_element(
            By.CSS_SELECTOR, second_team_next_game_location_selector).text.strip()

        return next_game_info
        # TODO: handle word "dias" in days strings
    except NoSuchElementException as e:
        print("Error locating the info about the next game. Returned empty dict.")
        return {}


def get_odd_even_stats(driver: webdriver.Chrome) -> dict | None:
    odd_even_stats = {}
    try:
        odd_even_stats['first_team_total_nepar'] = driver.find_element(
            By.CSS_SELECTOR, first_team_total_nepar_selector).text.strip()
        odd_even_stats['first_team_total_par'] = driver.find_element(
            By.CSS_SELECTOR, first_team_total_par_selector).text.strip()

        odd_even_stats['first_team_at_home_nepar'] = driver.find_element(
            By.CSS_SELECTOR, first_team_at_home_nepar_selector).text.strip()
        odd_even_stats['first_team_at_home_par'] = driver.find_element(
            By.CSS_SELECTOR, first_team_at_home_par_selector).text.strip()

        odd_even_stats['second_team_total_nepar'] = driver.find_element(
            By.CSS_SELECTOR, second_team_total_nepar_selector).text.strip()
        odd_even_stats['second_team_total_par'] = driver.find_element(
            By.CSS_SELECTOR, second_team_total_par_selector).text.strip()

        odd_even_stats['second_team_away_nepar'] = driver.find_element(
            By.CSS_SELECTOR, second_team_away_nepar_selector).text.strip()
        odd_even_stats['second_team_away_par'] = driver.find_element(
            By.CSS_SELECTOR, second_team_away_par_selector).text.strip()

        return odd_even_stats
    except NoSuchElementException as e:
        print(f"Error odd even {e}. Returned empty dict")
        return {}


def get_h2h_stats(driver: webdriver.Chrome) -> dict | None:
    h2h_stats = {}

    try:
        h2h_stats['first_team_scoring_average_last_14'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_scoring_average_last_14_selector).text.strip())
        h2h_stats['first_team_conceding_average_last_14'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_conceding_average_last_14_selector).text.strip())

        h2h_stats['second_team_scoring_average_last_14'] = float(driver.find_element(
            By.CSS_SELECTOR, second_team_scoring_average_last_14_selector).text.strip())
        h2h_stats['second_team_conceding_average_last_14'] = driver.find_element(
            By.CSS_SELECTOR, second_team_conceding_average_last_14_selector).text.strip()

        h2h_stats['first_team_scoring_average_at_home_last_7'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_scoring_average_at_home_last_7_selector).text.strip())
        h2h_stats['first_team_conceding_average_at_home_last_7'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_conceding_average_at_home_last_7_selector).text.strip())

        h2h_stats['second_team_scoring_average_away_last_7'] = float(driver.find_element(
            By.CSS_SELECTOR, second_team_scoring_average_away_last_7_selector).text.strip())
        h2h_stats['second_team_conceding_average_away_last_7'] = float(driver.find_element(
            By.CSS_SELECTOR, second_team_conceding_average_away_last_7_selector).text.strip())

        h2h_stats['first_team_scoring_average_last_6'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_scoring_average_last_6_selector).text.strip())
        h2h_stats['first_team_conceding_average_last_6'] = float(driver.find_element(
            By.CSS_SELECTOR, first_team_conceding_average_last_6_selector).text.strip())

        h2h_stats['second_team_scoring_average_last_6'] = float(driver.find_element(
            By.CSS_SELECTOR, second_team_scoring_average_last_6_selector).text.strip())
        h2h_stats['second_team_conceding_average_last_6'] = float(driver.find_element(
            By.CSS_SELECTOR, second_team_conceding_average_last_6_selector).text.strip())

        return h2h_stats
    except NoSuchElementException as e:
        print(f"Error h2h {e}. Returned empty object")
        return {}


def main():

    start_id = 2424424
    end_id = 2424425
    starter_url = "https://www.futebolscore.com/match/h2h-"

    data_list = []

    id = start_id
    while id <= end_id:
        delay = random.uniform(1, 4)
        time.sleep(delay)

        print(f"Fetching url with id={id} ...")

        try:
            id_dict = {"id": id}
            data = get_data(get_url(starter_url, id))
            data_list.append(data)
            print(f"Page with id={id} success !")
        except Exception as e:
            print(f"Error getting data from match {id},\n{e}")
        finally:
            id += 1

    df = pd.DataFrame(data_list)
    df.to_csv(f"./data/data_{start_id}_{end_id}.csv", index=False)


if __name__ == "__main__":
    main()
