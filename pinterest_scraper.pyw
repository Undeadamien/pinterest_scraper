import os
import pathlib
import random
import re

import requests
import selenium.common.exceptions as SE
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome
from urllib3.exceptions import ReadTimeoutError

GOOGLE_URL: str = "https://accounts.google.com/"
PINTEREST_URL: str = "https://www.pinterest.com"

EMAIL: str = ""
PASSWORD: str = ""

OUTPUT_FOLDER: pathlib.Path = pathlib.Path(__file__).resolve().parent / "output"
AMOUNT: int = 5
SEARCH: str = ""


def connect_to_google(
    driver: Chrome, wait: WebDriverWait, email: str, password: str
) -> None:
    driver.get(GOOGLE_URL)

    wait.until(EC.element_to_be_clickable((By.NAME, "identifier")))
    email_input = driver.find_element(By.NAME, "identifier")
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)

    wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
    password_input = driver.find_element(By.NAME, "Passwd")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)


def connect_to_pinterest(driver: Chrome, wait: WebDriverWait) -> None:
    driver.get(PINTEREST_URL)
    # wait for profile picture to load refresh if needed
    try:
        profile_picture_xpath = "//*[@class='hCL kVc L4E MIw']"
        wait.until(EC.presence_of_element_located((By.XPATH, profile_picture_xpath)))
    except SE.TimeoutException:
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.XPATH, profile_picture_xpath)))


def fetch_image_srcs(
    driver: Chrome,
    wait: WebDriverWait,
    action: ActionChains,
    amount: int,
    sample_size: int = 50,  # min size from which to sample
) -> list[str]:
    sample_size = max(amount, sample_size)
    image_xpath = "//img[@srcset]"
    srcs = set()

    # collect links into srcs
    while True:
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, image_xpath)))
            images = driver.find_elements(By.XPATH, f"{image_xpath}")
            for image in images:
                jpgs = re.findall(r"https[^ ]+jpg", image.get_property("srcset"))
                srcs.add(jpgs[-1])
                if len(srcs) >= sample_size:
                    break
            else:
                action.move_to_element(images[-1]).perform()
                continue
            break

        except SE.StaleElementReferenceException as exception:
            print(exception)
            continue
        except SE.TimeoutException as exception:
            print(exception)
            continue

    selected = random.sample(list(srcs), amount)
    return selected


def save_images(image_urls: list[str], destination_folder: pathlib.Path) -> None:
    for url in image_urls:
        name = url.split("/")[-1]
        path = destination_folder / name

        try:
            with open(path, "wb") as file:
                file.write(requests.get(url, timeout=20).content)
            print(f"{name} saved")

        except ReadTimeoutError:
            continue


def insert_search(driver: Chrome, wait: WebDriverWait, key_words: str) -> None:
    search_box_xpath = "//input[@name='searchBoxInput']"
    wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
    search_box = driver.find_element(By.XPATH, search_box_xpath)
    search_box.click()
    search_box.send_keys(key_words)
    search_box.send_keys(Keys.RETURN)


def initialize_web_driver() -> Chrome:
    driver = Chrome()
    driver.maximize_window()
    return driver


def main() -> None:
    if not OUTPUT_FOLDER.exists():
        OUTPUT_FOLDER.mkdir()

    with initialize_web_driver() as driver:
        wait = WebDriverWait(driver, 30)
        action = ActionChains(driver)

        connect_to_google(driver, wait, EMAIL, PASSWORD)
        connect_to_pinterest(driver, wait)
        if SEARCH:
            insert_search(driver, wait, SEARCH)
        image_srcs = fetch_image_srcs(driver, wait, action, AMOUNT)
        save_images(image_srcs, OUTPUT_FOLDER)

    os.startfile(OUTPUT_FOLDER)


if __name__ == "__main__":
    try:
        main()
    except OSError:
        pass
