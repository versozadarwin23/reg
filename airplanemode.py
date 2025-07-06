import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options # Import Options for headless mode


url = "http://192.168.254.254/index.html#index_status"
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--disable-gpu") # Recommended for headless mode on some systems
chrome_options.add_argument("--window-size=1920x1080") # Set a window size, as headless might default to a small one
chrome_options.add_argument("--no-sandbox") # Required if running as root in some environments (e.g., Docker)
chrome_options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems in some environments
driver = webdriver.Chrome(options=chrome_options)
try:
    driver.get(url)
except:
    pass
while True:
    try:
        login_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginlink")))
        break
    except:
        pass
try:
    login_link.click()
except:
    pass
try:
    # Wait for the username field to be present after clicking login
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "txtUsr"))
    )
except:
    pass
try:
    password_field = driver.find_element(By.ID, "txtPwd") # Assuming txtPwd appears with txtUsr
except:
    pass
try:
    username_field.send_keys("user")
except:
    pass
try:
    password_field.send_keys("@l03e1t3")
except:
    pass
try:
    # Click the login button
    driver.find_element(By.ID, "btnLogin").click()
except:
    pass
try:
    # Wait for the restart button to be clickable after successful login
    restart_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Restart Device' and @type='button']")))
except:
    pass
try:
    restart_button.click()
except:
    pass
try:
    restart_buttons = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "yesbtn")))
except:
    pass
try:
    restart_buttons.click()
except Exception as e:
    pass
finally:
    print("Airplane Mode Done")
    driver.quit()