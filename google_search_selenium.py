#!/usr/bin/env python3
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def main():
    options = webdriver.ChromeOptions()
    # Auto-enable headless in CI or when HEADLESS=1
    if os.getenv("CI") == "true" or os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    try:
        driver.get("https://www.google.com")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("jennie")
        search_box.submit()
        time.sleep(5)
        driver.save_screenshot("search_results.png")
        print("Saved screenshot: search_results.png")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
