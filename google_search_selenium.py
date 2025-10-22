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
        # Use classic headless for broader driver compatibility
        # and set an explicit window size to avoid blank screenshots.
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,2000")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    try:
        driver.get("https://www.google.com")
        # Wait for the search box to be present before interacting
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("jennie")
        search_box.submit()
        # Wait until search results container appears
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )

        # Try normal screenshot first
        ok = driver.save_screenshot("search_results.png")
        if not ok:
            # Fallback via Chrome DevTools Protocol to avoid None base64 issues
            try:
                result = driver.execute_cdp_cmd(
                    "Page.captureScreenshot", {"format": "png", "fromSurface": True}
                )
                if result and result.get("data"):
                    import base64

                    with open("search_results.png", "wb") as f:
                        f.write(base64.b64decode(result["data"]))
                else:
                    raise RuntimeError("CDP capture returned no data")
            except Exception as cdp_err:
                raise RuntimeError(
                    f"Failed to capture screenshot via WebDriver and CDP: {cdp_err}"
                )
        print("Saved screenshot: search_results.png")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
