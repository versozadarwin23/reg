from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os

# Set up Firefox options for headless mode
options = Options()
options.add_argument("--headless")

# Specify the path to geckodriver (kung hindi nasa PATH)
# DRIVER_PATH = "/data/data/com.termux/files/usr/bin/geckodriver" # Example path
# service = webdriver.FirefoxService(executable_path=DRIVER_PATH)
# driver = webdriver.Firefox(service=service, options=options)

# Initialize the WebDriver
driver = webdriver.Firefox(options=options)

# Example automation
driver.get("https://www.bing.com")
print(f"Page title: {driver.title}")

# Take a screenshot (opsyonal)
screenshot_path = "/sdcard/Download/termux_firefox_screenshot.png"
try:
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to: {screenshot_path}")
except Exception as e:
    print(f"Error saving screenshot: {e}")

driver.quit()
print("Browser closed.")
