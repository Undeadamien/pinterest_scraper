from os import startfile
from os.path import exists, join, dirname
from random import sample

import requests
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from undetected_chromedriver import Chrome


OUTPUT_FOLDER: str = join(dirname(__file__), "output")
EMAIL: str = "tralaundeadamien@gmail.com"
PASSWORD: str = "Polska2p"
AMOUNT: int = 10

assert exists(OUTPUT_FOLDER)


def connect_to_pinterest(driver: Chrome, wait: WebDriverWait):

    driver.get("https://www.pinterest.com")

    try:  # assure that we are connect by checking the profile picture
        xpath = "//*[@class='hCL kVc L4E MIw']"
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
    except TimeoutError:  # reload to retry
        driver.refresh()


def connect_to_google(driver: Chrome, wait: WebDriverWait):

    driver.get("https://accounts.google.com/")

    # insert the email
    wait.until(EC.visibility_of_element_located((By.NAME, "identifier")))
    id_input = driver.find_element(By.NAME, "identifier")
    id_input.send_keys(EMAIL)
    id_input.send_keys(Keys.RETURN)

    # insert the password
    wait.until(EC.visibility_of_element_located((By.NAME, "Passwd")))
    pass_input = driver.find_element(By.NAME, "Passwd")
    pass_input.send_keys(PASSWORD)
    pass_input.send_keys(Keys.RETURN)

    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*")))


def fetched_srcs(driver: Chrome, wait: WebDriverWait, amount):

    xpath = "//img[@srcset]"
    wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
    images = driver.find_elements(By.XPATH, xpath)
    srcs = []

    # from the scrs we retrieve the src, to the largest jpg image
    for image in images:
        links = [link.strip() for link in image.get_attribute("srcset").split()
                 if link.strip().endswith(".jpg")]
        srcs.append(links[-1])

    if amount > len(srcs):
        amount = len(srcs)

    return sample(srcs, amount)


def save_images(image_urls: list[str], destination_folder: str):

    for url in image_urls:

        name = url.split("/")[-1]
        path = f"{destination_folder}\\{name}"

        if exists(path):
            print(f"{name} already exist")
            continue

        with open(path, "wb") as file:
            file.write(requests.get(url, timeout=10).content)

        print(f"{name} saved")


def main():

    driver = Chrome()
    wait = WebDriverWait(driver, 60)
    driver.maximize_window()

    connect_to_google(driver, wait)
    connect_to_pinterest(driver, wait)

    selected_images = fetched_srcs(driver, wait, AMOUNT)
    save_images(selected_images, OUTPUT_FOLDER)

    startfile(OUTPUT_FOLDER)


if __name__ == "__main__":
    main()