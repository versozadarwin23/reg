from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

# Set up Chrome options for headless mode in Termux
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# Kailangan ng virtual display kapag hindi --headless ang mode
# Pero kung gusto mo ng ganap na headless (walang graphical window),
# gamitin ang --headless=new o --headless.
options.add_argument("--headless=new") # Mas bagong headless mode

# Kung may isyu sa --headless, maaaring subukan ito para sa virtual display
# os.environ['DISPLAY'] = ':1' # Halimbawa lang, depende sa iyong setup
# options.add_argument("--display=:1")

# Specify the path to chromedriver (if not in PATH)
# Kadalasan, kung ininstall mo ang chromium sa Termux, kasama na ang chromedriver sa PATH.
# Kung hindi, maaaring kailangan mong i-specify ang path:
# DRIVER_PATH = "/data/data/com.termux/files/usr/bin/chromedriver" # Example path
# driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)

# Initialize the WebDriver
driver = webdriver.Chrome(options=options)

# Example automation
driver.get("https://www.google.com")
print(f"Page title: {driver.title}")

# Take a screenshot (opsyonal)
screenshot_path = "/sdcard/Download/termux_screenshot.png"
try:
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to: {screenshot_path}")
except Exception as e:
    print(f"Error saving screenshot: {e}")

driver.quit()
print("Browser closed.")
