from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selectors.current_form_averages_selectors import *
from selectors.general_info_selectors import *
from selectors.next_game_days_until_location_selectors import *
from selectors.last_game_days_since_location_selectors import *
import time
import random
import pandas as pd
import os
import concurrent.futures
import threading
from utils.functions import (
    calculate_days_difference,
    get_team_next_game_location,
    get_team_last_game_location,
    click_element,
    find_element_text,
    find_element_by_css,
)
from utils.ids import get_ids
from utils.urls import get_match_url
from utils.args import parse_args
from utils.driver import config_driver

# import requests
# import re
# from datetime import date


def get_data(url: str) -> dict:
    driver = config_driver()
    driver.get(url)

    time.sleep(0.25)

    data = {}

    general_info = get_match_general_info(driver)

    if general_info is None:
        raise Exception("Current match is from extra low league.")

    last_game_info = get_last_game_info(
        driver,
        general_info["first_team_name"],
        general_info["second_team_name"],
        general_info["date_time"],
    )
    next_game_info = get_next_game_info(driver)
    current_form_averages = get_current_form_averages(driver)

    if (
        last_game_info is None
        or next_game_info is None
        or current_form_averages is None
    ):
        raise Exception("Current match is from extra low league.")

    data.update(general_info)
    data.update(last_game_info)
    data.update(next_game_info)
    data.update(current_form_averages)

    print(len(data.keys()))

    return data


def get_match_general_info(driver: webdriver.Chrome) -> dict | None:
    general_info = {}

    try:
        general_info["first_team_name"] = find_element_text(
            driver, first_team_name_selector
        )
        general_info["second_team_name"] = find_element_text(
            driver, second_team_name_selector
        )

        general_info["league_name"] = find_element_text(driver, league_name_selector)
        general_info["date_time"] = find_element_text(driver, date_time_selector)

        general_info["first_team_goals_final_score"] = find_element_text(
            driver, first_team_goals_scored_selector
        )
        general_info["second_team_goals_final_score"] = find_element_text(
            driver, second_team_goals_scored_selector
        )
        general_info["game_state"] = find_element_text(driver, game_state_selector)

        return general_info
    except Exception as e:
        print(f"Error locating general info section.\n{e}")
        return None


def get_last_game_info(
    driver: webdriver.Chrome,
    first_team_name: str,
    second_team_name: str,
    date_time: str,
) -> dict | None:
    last_game_info = {}
    try:
        first_team_last_game_date = find_element_text(
            driver, first_team_last_game_date_selector
        )
        second_team_last_game_date = find_element_text(
            driver, second_team_last_game_date_selector
        )

        last_game_info["first_team_days_since_last_game"] = calculate_days_difference(
            first_team_last_game_date, date_time
        )
        last_game_info["second_team_days_since_last_game"] = calculate_days_difference(
            second_team_last_game_date, date_time
        )

        last_game_info["first_team_last_game_location"] = get_team_last_game_location(
            find_element_by_css(driver, was_first_team_last_game_at_home_selector),
            first_team_name,
        )
        last_game_info["second_team_last_game_location"] = get_team_last_game_location(
            find_element_by_css(driver, was_second_team_last_game_at_home_selector),
            second_team_name,
        )

        return last_game_info
    except NoSuchElementException as e:
        print(f"Error locating last-game info section:\n{e}")
        return None


def get_next_game_info(driver: webdriver.Chrome) -> dict | None:
    next_game_info = {}

    try:
        next_game_info["first_team_days_until_next_game"] = find_element_text(
            driver, first_team_days_until_next_game_selector
        )
        next_game_info["second_team_days_until_next_game"] = find_element_text(
            driver, second_team_days_until_next_game_selector
        )

        next_game_info["first_team_next_game_location"] = get_team_next_game_location(
            find_element_by_css(driver, is_first_team_next_game_at_home_selector)
        )
        next_game_info["second_team_next_game_location"] = get_team_next_game_location(
            find_element_by_css(driver, is_second_team_next_game_at_home_selector)
        )

        return next_game_info

    except NoSuchElementException as e:
        print(f"Error locating next-game info section:\n{e}")
        return None


def get_current_form_averages(driver: webdriver.Chrome) -> dict | None:
    current_form_averages = {}

    try:
        # All leagues, home+away

        current_form_averages["first_team_total_scoring_average"] = float(
            find_element_text(driver, first_team_scoring_average_selector)
        )
        current_form_averages["second_team_total_scoring_average"] = float(
            find_element_text(driver, second_team_scoring_average_selector)
        )
        current_form_averages["first_team_total_conceding_average"] = float(
            find_element_text(driver, first_team_conceding_average_selector)
        )
        current_form_averages["second_team_total_conceding_average"] = float(
            find_element_text(driver, second_team_conceding_average_selector)
        )

        # Same league, home+away

        click_element(driver, same_league_button_selector)

        current_form_averages["first_team_same_league_scoring_average"] = float(
            find_element_text(driver, first_team_scoring_average_selector)
        )
        current_form_averages["second_team_same_league_scoring_average"] = float(
            find_element_text(driver, second_team_scoring_average_selector)
        )
        current_form_averages["first_team_same_league_conceding_average"] = float(
            find_element_text(driver, first_team_conceding_average_selector)
        )
        current_form_averages["second_team_same_league_conceding_average"] = float(
            find_element_text(driver, second_team_conceding_average_selector)
        )

        # All leagues, grouped by home/away

        click_element(driver, same_league_button_selector)
        click_element(driver, correct_home_away_button_selector)

        current_form_averages["first_team_at_home_scoring_average"] = float(
            find_element_text(driver, first_team_scoring_average_selector)
        )
        current_form_averages["second_team_away_scoring_average"] = float(
            find_element_text(driver, second_team_scoring_average_selector)
        )
        current_form_averages["first_team_at_home_conceding_average"] = float(
            find_element_text(driver, first_team_conceding_average_selector)
        )
        current_form_averages["second_team_away_conceding_average"] = float(
            find_element_text(driver, second_team_conceding_average_selector)
        )

        # Same league, grouped by home/away

        click_element(driver, same_league_button_selector)

        current_form_averages["first_team_same_league_at_home_scoring_average"] = float(
            find_element_text(driver, first_team_scoring_average_selector)
        )
        current_form_averages["second_team_same_league_away_scoring_average"] = float(
            find_element_text(driver, second_team_scoring_average_selector)
        )
        current_form_averages["first_team_same_league_at_home_conceding_average"] = (
            float(find_element_text(driver, first_team_conceding_average_selector))
        )
        current_form_averages["second_team_same_league_away_conceding_average"] = float(
            find_element_text(driver, second_team_conceding_average_selector)
        )

        return current_form_averages
    except NoSuchElementException as e:
        print(f"Error locating current form section:\n{e}")
        return None


def fetch_and_save_data(id: int, file_path: str, lock: threading.Lock) -> None:
    try:
        delay = random.uniform(2, 7)
        time.sleep(delay)

        print(f"Fetching url with id={id} ...")

        data: dict = get_data(get_match_url(id))
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


def main() -> None:
    start_time = time.time()
    args = parse_args()

    start_id: int | None = args.s
    end_id: int | None = args.e
    file_path: str = args.f
    num_threads: int = args.t

    lock = threading.Lock()

    ids = get_ids(start_id, end_id)

    if ids is None:
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda id: fetch_and_save_data(id, file_path, lock), ids)

    total_time = time.time() - start_time
    print(f"Finished in: {total_time:.2f} seconds / {total_time/60:.2f} minutes")


if __name__ == "__main__":
    main()
