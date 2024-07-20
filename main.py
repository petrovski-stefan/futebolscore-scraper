import time
import random
import pandas as pd
import os
import concurrent.futures
import threading
from utils.Scraper import Scraper
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

    scraper = Scraper(driver)

    general_info = scraper.get_match_general_info()

    if general_info is None:
        raise Exception("Current match is from extra low league.")

    last_game_info = scraper.get_last_game_info(
        general_info["first_team_name"],
        general_info["second_team_name"],
        general_info["date_time"],
    )
    next_game_info = scraper.get_next_game_info()
    current_form_averages = scraper.get_current_form_averages()

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
