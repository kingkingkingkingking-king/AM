"""
speed_test_tool.py — Measures internet speed using fast.com via Selenium.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SpeedTestTool:
    _CHROME_OPTIONS = [
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1920,1080",
    ]

    def run_test(self) -> str:
        """
        Launches a headless Chrome session, runs fast.com, and returns
        a speed string like "45 Mbps".  Driver is always cleaned up.
        """
        options = Options()
        for opt in self._CHROME_OPTIONS:
            options.add_argument(opt)

        driver = webdriver.Chrome(options=options)
        try:
            driver.get("https://fast.com")
            wait = WebDriverWait(driver, 60)

            # Wait for the speed value to appear and stabilise
            wait.until(EC.presence_of_element_located((By.ID, "speed-value")))
            wait.until(lambda d: d.find_element(By.ID, "speed-value").text != "")

            speed = driver.find_element(By.ID, "speed-value").text
            unit  = driver.find_element(By.ID, "speed-units").text
            return f"{speed} {unit}"

        except Exception as e:
            return f"Speed test failed: {e}"

        finally:
            driver.quit()


if __name__ == "__main__":
    print("Running speed test...")
    result = SpeedTestTool().run_test()
    print("Speed:", result)
