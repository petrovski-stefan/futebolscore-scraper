from .driver import config_driver
from .constants import FIXTURES_URL
from bs4 import BeautifulSoup, ResultSet, Tag
from .functions import click_date, click_sort_by_time, click_show_all, click_tz
from selectors.fixtures_selectors import *
import re
import time


def get_ids(
    start_id: int | None, end_id: int | None, today: bool, tomorrow: bool
) -> range | list[str] | None:
    if start_id and end_id and start_id <= end_id and not today and not tomorrow:
        return range(start_id, end_id + 1)
    elif today and not start_id and not end_id:
        return get_pred_ids(True)
    elif tomorrow and not start_id and not end_id:
        return get_pred_ids(False)
    else:
        print("Error entering the arguments. Try again!")


def get_pred_ids(is_for_today: bool) -> list:
    driver = config_driver()
    driver.get(FIXTURES_URL)

    driver.refresh()
    time.sleep(1)

    click_tz(driver)
    click_date(driver, is_for_today)
    click_sort_by_time(driver)
    click_show_all(driver)

    html = driver.page_source
    driver.quit()
    bs = BeautifulSoup(html, "html.parser")
    rows = bs.select(rows_selector)
    idss = save_fixtures(rows)

    return idss


def save_fixtures(rows: ResultSet[Tag]) -> list[str]:
    print(len(rows))
    league_name = None
    idss = []
    # cleaned_leagues = get_cleaned_ai_leagues(LEAGUES)

    for i in range(0, len(rows)):
        curr_row_id = rows[i].get_attribute_list("id")[0]

        if curr_row_id is None:
            continue

        # League row
        if curr_row_id.startswith("tr_"):
            league_name_span = rows[i].select_one(league_name_span_selector)

            if league_name_span is not None:
                # TODO: replace chars
                league_name = league_name_span.text.strip()

        elif (
            curr_row_id.startswith("tr1_")
            and league_name is not None
            # and league_name in cleaned_leagues
        ):  # Match row
            match_id = re.findall(r"\d{7}", curr_row_id)[0]
            score = rows[i].select_one(".handpoint.f-b.blue")
            if score and score.text == " - ":
                idss.append(match_id)

    return idss
