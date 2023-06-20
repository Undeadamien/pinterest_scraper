import re
from os import startfile
from pathlib import Path
from random import sample

import requests
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome
from urllib3.exceptions import ReadTimeoutError

OUTPUT_FOLDER = Path(__file__).resolve().parent / "output"
EMAIL = ""
PASSWORD = ""
AMOUNT = 5

GOOGLE_URL = "https://accounts.google.com/"
PINTEREST_URL = "https://www.pinterest.com"


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

    try:
        profile_picture_xpath = "//*[@class='hCL kVc L4E MIw']"
        wait.until(EC.visibility_of_element_located((By.XPATH, profile_picture_xpath)))

    except TimeoutException:
        driver.refresh()


def fetch_image_srcs(driver: Chrome, wait: WebDriverWait, amount: int) -> list[str]:
    image_xpath = "//img[@srcset]"
    wait.until(EC.presence_of_all_elements_located((By.XPATH, image_xpath)))
    images = driver.find_elements(By.XPATH, image_xpath)

    srcs = []

    for image in images:
        try:
            string = image.get_property("srcset")
            jpgs = re.findall(r"https[^ ]+jpg", string)
            if jpgs:
                srcs.append(jpgs[-1])
        except StaleElementReferenceException:
            continue

    return sample(srcs, min(amount, len(srcs)))


def save_images(image_urls: list[str], destination_folder: str) -> None:
    for url in image_urls:
        name = url.split("/")[-1]
        path = destination_folder / name

        try:
            with open(path, "wb") as file:
                file.write(requests.get(url, timeout=20).content)
        except ReadTimeoutError:
            continue

        print(f"{name} saved")


def insert_search(driver: Chrome, wait: WebDriverWait, key_words: str) -> None:
    search_box_xpath = "//input[@name='searchBoxInput']"
    wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
    search_box = driver.find_element(By.XPATH, search_box_xpath)
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
        wait = WebDriverWait(driver, 120)
        connect_to_google(driver, wait, EMAIL, PASSWORD)
        connect_to_pinterest(driver, wait)
        image_srcs = fetch_image_srcs(driver, wait, AMOUNT)
        save_images(image_srcs, OUTPUT_FOLDER)

    startfile(str(OUTPUT_FOLDER))


if __name__ == "__main__":
    main()
