import os
import time
import random
import concurrent.futures
import threading
from dotenv import load_dotenv
from utils.Scraper import Scraper
from utils.ids import get_ids
from utils.urls import get_match_url
from utils.args import parse_args
from utils.driver import config_driver
from utils.df import write_to_df
from utils.functions import get_ai_website_session, get_match_stats, make_prediction


def get_data(
    url: str, is_for_prediction: bool, cookie: dict | None, ai_url: str
) -> dict:
    driver = config_driver()
    driver.get(url)

    time.sleep(0.25)

    data = {}

    scraper = Scraper(driver)

    general_info = scraper.get_match_general_info(is_for_prediction)
    if general_info is None:
        raise Exception("Current match is from extra low league.")

    data.update(general_info)
    # if is_for_prediction and cookie is None:
    #     raise Exception("Cookie not sent")
    if not is_for_prediction:
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

        # TODO: use unpacking
        data.update(last_game_info)
        data.update(next_game_info)
        data.update(current_form_averages)
    elif cookie is not None:
        home_last5_str, away_last5_str = get_match_stats(url, driver)
        prediction = make_prediction(home_last5_str, away_last5_str, ai_url, cookie)
        time.sleep(3)
        data.update({"prediction": prediction})

    print(len(data.keys()))

    return data


def fetch_and_save_data(
    id: int,
    file_path: str,
    lock: threading.Lock,
    is_prediction: bool = False,
    cookie: dict | None = None,
    ai_url: str | None = None,
) -> None:
    try:
        delay = random.uniform(2, 7)
        time.sleep(delay)

        print(f"Fetching url with id={id} ...")

        data = get_data(
            get_match_url(id),
            is_prediction,
            cookie,
            ai_url if ai_url is not None else "",
        )
        data.update({"id": id})

        with lock:
            write_to_df(file_path, data)

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
    today: bool = args.today
    tomorrow: bool = args.tomorrow

    lock = threading.Lock()

    ids = get_ids(start_id, end_id, today, tomorrow)

    if ids is None:
        return
    load_dotenv()
    is_prediction = today or tomorrow
    cookie = None

    ai_url = None
    if is_prediction:
        cookie = get_ai_website_session()
        ai_url = os.getenv("AI_PREDICTIONS_URL")
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(
            lambda id: fetch_and_save_data(
                id, file_path, lock, is_prediction, cookie, ai_url
            ),
            ids,
        )

    total_time = time.time() - start_time
    print(f"Finished in: {total_time:.2f} seconds / {total_time/60:.2f} minutes")


if __name__ == "__main__":
    main()
