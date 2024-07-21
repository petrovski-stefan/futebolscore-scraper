from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from .functions import (
    find_element_text,
    click_element,
    calculate_days_difference,
    find_element_by_css,
    get_team_last_game_location,
    get_team_next_game_location,
)
from selectors.current_form_averages_selectors import *
from selectors.general_info_selectors import *
from selectors.next_game_days_until_location_selectors import *
from selectors.last_game_days_since_location_selectors import *


class Scraper:
    def __init__(self, driver: webdriver.Chrome) -> None:
        self.driver = driver

    def get_match_general_info(self, is_for_prediction: bool = False) -> dict | None:
        general_info = {}

        try:
            general_info["first_team_name"] = find_element_text(
                self.driver, first_team_name_selector
            )
            general_info["second_team_name"] = find_element_text(
                self.driver, second_team_name_selector
            )

            general_info["league_name"] = find_element_text(
                self.driver, league_name_selector
            )
            general_info["date_time"] = find_element_text(
                self.driver, date_time_selector
            )

            if not is_for_prediction:
                general_info["first_team_goals_final_score"] = find_element_text(
                    self.driver, first_team_goals_scored_selector
                )
                general_info["second_team_goals_final_score"] = find_element_text(
                    self.driver, second_team_goals_scored_selector
                )
                general_info["game_state"] = find_element_text(
                    self.driver, game_state_selector
                )

            return general_info
        except Exception as e:
            print(f"Error locating general info section.\n{e}")
            return None

    def get_last_game_info(
        self,
        first_team_name: str,
        second_team_name: str,
        date_time: str,
    ) -> dict | None:
        last_game_info = {}
        try:
            first_team_last_game_date = find_element_text(
                self.driver, first_team_last_game_date_selector
            )
            second_team_last_game_date = find_element_text(
                self.driver, second_team_last_game_date_selector
            )

            last_game_info["first_team_days_since_last_game"] = (
                calculate_days_difference(first_team_last_game_date, date_time)
            )
            last_game_info["second_team_days_since_last_game"] = (
                calculate_days_difference(second_team_last_game_date, date_time)
            )

            last_game_info["first_team_last_game_location"] = (
                get_team_last_game_location(
                    find_element_by_css(
                        self.driver, was_first_team_last_game_at_home_selector
                    ),
                    first_team_name,
                )
            )
            last_game_info["second_team_last_game_location"] = (
                get_team_last_game_location(
                    find_element_by_css(
                        self.driver, was_second_team_last_game_at_home_selector
                    ),
                    second_team_name,
                )
            )

            return last_game_info
        except NoSuchElementException as e:
            print(f"Error locating last-game info section:\n{e}")
            return None

    def get_next_game_info(self) -> dict | None:
        next_game_info = {}

        try:
            next_game_info["first_team_days_until_next_game"] = find_element_text(
                self.driver, first_team_days_until_next_game_selector
            )
            next_game_info["second_team_days_until_next_game"] = find_element_text(
                self.driver, second_team_days_until_next_game_selector
            )

            next_game_info["first_team_next_game_location"] = (
                get_team_next_game_location(
                    find_element_by_css(
                        self.driver, is_first_team_next_game_at_home_selector
                    )
                )
            )
            next_game_info["second_team_next_game_location"] = (
                get_team_next_game_location(
                    find_element_by_css(
                        self.driver, is_second_team_next_game_at_home_selector
                    )
                )
            )

            return next_game_info

        except NoSuchElementException as e:
            print(f"Error locating next-game info section:\n{e}")
            return None

    def get_current_form_averages(self) -> dict | None:
        current_form_averages = {}

        try:
            # All leagues, home+away

            current_form_averages["first_team_total_scoring_average"] = float(
                find_element_text(self.driver, first_team_scoring_average_selector)
            )
            current_form_averages["second_team_total_scoring_average"] = float(
                find_element_text(self.driver, second_team_scoring_average_selector)
            )
            current_form_averages["first_team_total_conceding_average"] = float(
                find_element_text(self.driver, first_team_conceding_average_selector)
            )
            current_form_averages["second_team_total_conceding_average"] = float(
                find_element_text(self.driver, second_team_conceding_average_selector)
            )

            # Same league, home+away

            click_element(self.driver, same_league_button_selector)

            current_form_averages["first_team_same_league_scoring_average"] = float(
                find_element_text(self.driver, first_team_scoring_average_selector)
            )
            current_form_averages["second_team_same_league_scoring_average"] = float(
                find_element_text(self.driver, second_team_scoring_average_selector)
            )
            current_form_averages["first_team_same_league_conceding_average"] = float(
                find_element_text(self.driver, first_team_conceding_average_selector)
            )
            current_form_averages["second_team_same_league_conceding_average"] = float(
                find_element_text(self.driver, second_team_conceding_average_selector)
            )

            # All leagues, grouped by home/away

            click_element(self.driver, same_league_button_selector)
            click_element(self.driver, correct_home_away_button_selector)

            current_form_averages["first_team_at_home_scoring_average"] = float(
                find_element_text(self.driver, first_team_scoring_average_selector)
            )
            current_form_averages["second_team_away_scoring_average"] = float(
                find_element_text(self.driver, second_team_scoring_average_selector)
            )
            current_form_averages["first_team_at_home_conceding_average"] = float(
                find_element_text(self.driver, first_team_conceding_average_selector)
            )
            current_form_averages["second_team_away_conceding_average"] = float(
                find_element_text(self.driver, second_team_conceding_average_selector)
            )

            # Same league, grouped by home/away

            click_element(self.driver, same_league_button_selector)

            current_form_averages["first_team_same_league_at_home_scoring_average"] = (
                float(
                    find_element_text(self.driver, first_team_scoring_average_selector)
                )
            )
            current_form_averages["second_team_same_league_away_scoring_average"] = (
                float(
                    find_element_text(self.driver, second_team_scoring_average_selector)
                )
            )
            current_form_averages[
                "first_team_same_league_at_home_conceding_average"
            ] = float(
                find_element_text(self.driver, first_team_conceding_average_selector)
            )
            current_form_averages["second_team_same_league_away_conceding_average"] = (
                float(
                    find_element_text(
                        self.driver, second_team_conceding_average_selector
                    )
                )
            )

            return current_form_averages
        except NoSuchElementException as e:
            print(f"Error locating current form section:\n{e}")
            return None


# TODO: add marbo's bs4 scraper methods in this class
