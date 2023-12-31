from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selectors.current_form_averages_selectors import *
from selectors.general_info_selectors import *
from selectors.next_game_days_until_location_selectors import *
from selectors.last_game_days_since_location_selectors import *
import time
import random
import pandas as pd
import argparse
import os
import concurrent.futures
import threading
from utils.functions import calculate_days_difference, get_team_next_game_location, get_team_last_game_location, \
    get_random_agent, click_element, find_element_text, find_element_by_css
from utils.constants import agents


lock = threading.Lock()


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    agent = get_random_agent(agents)
    chrome_options.add_argument(f"--user-agent={agent}")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    return driver


def get_match_url(id: int) -> str:
    return f"https://www.futebolscore.com/jogos/computador-{id}"


def get_data(url: str) -> dict:
    driver = config_driver()
    driver.get(url)

    time.sleep(0.25)

    data = {}

    general_info = get_match_general_info(driver)

    if general_info == None:
        raise Exception(
            "Current match is from extra low league or a female match or scheduled for the future.")

    last_game_info = get_last_game_info(
        driver, general_info['first_team_name'], general_info['second_team_name'], general_info['date_time'])
    next_game_info = get_next_game_info(driver)
    current_form_averages = get_current_form_averages(driver)

    if last_game_info == None or next_game_info == None or current_form_averages == None:
        raise Exception(
            "Current match is from extra low league or a female match or scheduled for the future.")

    data.update(general_info)
    data.update(last_game_info)
    data.update(next_game_info)
    data.update(current_form_averages)

    print(len(data.keys()))

    return data


def get_match_general_info(driver: webdriver.Chrome) -> dict | None:
    general_info = {}

    try:
        general_info['first_team_name'] = find_element_text(
            driver, first_team_name_selector)
        general_info['second_team_name'] = find_element_text(
            driver, second_team_name_selector)

        general_info['league_name'] = find_element_text(
            driver, league_name_selector)
        general_info['date_time'] = find_element_text(
            driver, date_time_selector)

        general_info['first_team_goals_final_score'] = find_element_text(
            driver, first_team_goals_scored_selector)
        general_info['second_team_goals_final_score'] = find_element_text(
            driver, second_team_goals_scored_selector)

        general_info['game_state'] = find_element_text(
            driver, game_state_selector)

        return general_info
    except Exception as e:
        print(f"Error locating general info section. Returned None.\n{e}")
        return None


def get_last_game_info(driver: webdriver.Chrome, first_team_name: str, second_team_name: str, date_time: str) -> dict | None:
    last_game_info = {}
    try:
        first_team_last_game_date = find_element_text(
            driver, first_team_last_game_date_selector)
        second_team_last_game_date = find_element_text(
            driver, second_team_last_game_date_selector)

        last_game_info['first_team_days_since_last_game'] = calculate_days_difference(
            first_team_last_game_date, date_time)
        last_game_info['second_team_days_since_last_game'] = calculate_days_difference(
            second_team_last_game_date, date_time)

        last_game_info['first_team_last_game_location'] = get_team_last_game_location(
            find_element_by_css(driver, was_first_team_last_game_at_home_selector), first_team_name)
        last_game_info['second_team_last_game_location'] = get_team_last_game_location(
            find_element_by_css(driver, was_second_team_last_game_at_home_selector), second_team_name)

        return last_game_info
    except NoSuchElementException as e:
        print(f"Error locating last-game info section:\n{e}\nReturned None.")
        return None


def get_next_game_info(driver: webdriver.Chrome) -> dict | None:
    next_game_info = {}

    try:
        next_game_info['first_team_days_until_next_game'] = find_element_text(
            driver, first_team_days_until_next_game_selector)
        next_game_info['second_team_days_until_next_game'] = find_element_text(
            driver, second_team_days_until_next_game_selector)

        next_game_info['first_team_next_game_location'] = get_team_next_game_location(
            find_element_by_css(driver, is_first_team_next_game_at_home_selector))
        next_game_info['second_team_next_game_location'] = get_team_next_game_location(
            find_element_by_css(driver, is_second_team_next_game_at_home_selector))

        return next_game_info

    except NoSuchElementException as e:
        print(f"Error locating next-game info section:\n{e}\nReturned None.")
        return None


def get_current_form_averages(driver: webdriver.Chrome) -> dict | None:
    current_form_averages = {}

    try:
        # All leagues, home+away

        current_form_averages['first_team_total_scoring_average'] = float(
            find_element_text(driver, first_team_scoring_average_selector))
        current_form_averages['second_team_total_scoring_average'] = float(
            find_element_text(driver, second_team_scoring_average_selector))
        current_form_averages['first_team_total_conceding_average'] = float(
            find_element_text(driver, first_team_conceding_average_selector))
        current_form_averages['second_team_total_conceding_average'] = float(
            find_element_text(driver, second_team_conceding_average_selector))

        # Same league, home+away

        click_element(driver, same_league_button_selector)

        current_form_averages['first_team_same_league_scoring_average'] = float(
            find_element_text(driver, first_team_scoring_average_selector))
        current_form_averages['second_team_same_league_scoring_average'] = float(
            find_element_text(driver, second_team_scoring_average_selector))
        current_form_averages['first_team_same_league_conceding_average'] = float(
            find_element_text(driver, first_team_conceding_average_selector))
        current_form_averages['second_team_same_league_conceding_average'] = float(
            find_element_text(driver, second_team_conceding_average_selector))

        # All leagues, grouped by home/away

        click_element(driver, same_league_button_selector)
        click_element(driver, correct_home_away_button_selector)

        current_form_averages['first_team_at_home_scoring_average'] = float(
            find_element_text(driver, first_team_scoring_average_selector))
        current_form_averages['second_team_away_scoring_average'] = float(
            find_element_text(driver, second_team_scoring_average_selector))
        current_form_averages['first_team_at_home_conceding_average'] = float(
            find_element_text(driver, first_team_conceding_average_selector))
        current_form_averages['second_team_away_conceding_average'] = float(
            find_element_text(driver, second_team_conceding_average_selector))

        # Same league, grouped by home/away

        click_element(driver, same_league_button_selector)

        current_form_averages['first_team_same_league_at_home_scoring_average'] = float(
            find_element_text(driver, first_team_scoring_average_selector))
        current_form_averages['second_team_same_league_away_scoring_average'] = float(
            find_element_text(driver, second_team_scoring_average_selector))
        current_form_averages['first_team_same_league_at_home_conceding_average'] = float(
            find_element_text(driver, first_team_conceding_average_selector))
        current_form_averages['second_team_same_league_away_conceding_average'] = float(
            find_element_text(driver, second_team_conceding_average_selector))

        return current_form_averages
    except NoSuchElementException as e:
        print(f"Error locating current form section:\n{e}\nReturned None")
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape football statistics")
    parser.add_argument("start_id", type=int,
                        help="Lowest match id to be scraped")
    parser.add_argument("end_id", type=int,
                        help="Highest match id to be scraped")
    args = parser.parse_args()

    return args


def fetch_and_save_data(id: int, file_path: str):
    try:
        delay = random.uniform(2, 7)
        time.sleep(delay)

        print(f"Fetching url with id={id} ...")

        data: dict[str, int | str | float] = get_data(get_match_url(id))
        data.update({"id": id})

        with lock:
            if os.path.exists(file_path):
                old_df = pd.read_csv(file_path)
                new_df = pd.DataFrame([data])
                updated_df = pd.concat([old_df, new_df], ignore_index=True)
                updated_df.to_csv(file_path, index=False)
            else:
                new_df = pd.DataFrame([data])
                new_df.to_csv(file_path, index=False)

        print(f"Page with id={id} success !")
    except Exception as e:
        print(f"Error getting data from match {id},\n{e}")


def main():
    start = time.time()
    args = parse_args()

    start_id = args.start_id
    end_id = args.end_id

    print(args)

    file_path = "data/data.csv"
    ids = range(start_id, end_id+1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda id: fetch_and_save_data(id, file_path), ids)

    print(f"\nFinished in: {time.time() -
          start} seconds / {(time.time()-start)/60} minutes")
    print(f"Scraped from {start_id} to {end_id}")


if __name__ == "__main__":
    main()
