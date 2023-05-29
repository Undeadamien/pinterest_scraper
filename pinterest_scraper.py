import re
from os import mkdir, startfile
from os.path import dirname, exists, join
from random import sample

import requests
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome

OUTPUT_FOLDER: str = join(dirname(__file__), "output")
EMAIL: str = ""
PASSWORD: str = ""
AMOUNT: int = 10


def connect_to_google(driver: Chrome, wait: WebDriverWait):
    """Log into Google account, wouldn't be possible without undetected_chromedriver"""

    driver.get("https://accounts.google.com/")

    # insert the email
    wait.until(EC.element_to_be_clickable((By.NAME, "identifier")))
    id_input = driver.find_element(By.NAME, "identifier")
    id_input.send_keys(EMAIL)
    id_input.send_keys(Keys.RETURN)

    # insert the password
    wait.until(EC.element_to_be_clickable((By.NAME, "Passwd")))
    pass_input = driver.find_element(By.NAME, "Passwd")
    pass_input.send_keys(PASSWORD)
    pass_input.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*")))


def connect_to_pinterest(driver: Chrome, wait: WebDriverWait):
    """Log into Pinterest, to access user feed"""

    driver.get("https://www.pinterest.com")

    try:  # assure that we are connect by checking the profile picture
        xpath = "//*[@class='hCL kVc L4E MIw']"
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

    except TimeoutError:  # reload to retry
        driver.refresh()


def fetch_srcs(driver: Chrome, wait: WebDriverWait, amount) -> list[str]:
    """Fetch the largest jpg file from the srcs"""

    xpath = "//img[@srcset]"
    wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    images = driver.find_elements(By.XPATH, xpath)

    srcs = []

    for image in images:
        string = image.get_attribute("srcset")
        jpgs = re.findall(r"https[^ ]+jpg", string)
        srcs.append(jpgs[-1])

    return sample(srcs, amount)


def save_images(image_urls: list[str], destination_folder: str):
    for url in image_urls:
        name = url.split("/")[-1]
        path = f"{destination_folder}\\{name}"

        with open(path, "wb") as file:
            file.write(requests.get(url, timeout=10).content)

        print(f"{name} saved")


def insert_search(driver: Chrome, wait: WebDriverWait, key_words: str) -> None:
    """Insert key words into the search bar"""

    xpath = "//input[@name='searchBoxInput']"
    wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    search_box = driver.find_element(By.XPATH, xpath)
    search_box.send_keys(key_words)
    search_box.send_keys(Keys.RETURN)


def main():
    driver = Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 60)

    if not exists(OUTPUT_FOLDER):
        mkdir(join(dirname(__file__), "output"))

    connect_to_google(driver, wait)
    connect_to_pinterest(driver, wait)
    selected_src = fetch_srcs(driver, wait, AMOUNT)
    save_images(selected_src, OUTPUT_FOLDER)

    startfile(OUTPUT_FOLDER)


if __name__ == "__main__":
    main()
