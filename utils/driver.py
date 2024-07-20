from selenium import webdriver
from .constants import agents
from .functions import get_random_agent


def config_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    agent = get_random_agent(agents)
    chrome_options.add_argument(f"--user-agent={agent}")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    return driver
