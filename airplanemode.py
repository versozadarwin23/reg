from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options # Import Options for Firefox

url = "http://192.168.254.254/index.html#index_status"

# Set up Firefox options for headless mode
firefox_options = Options()
firefox_options.add_argument("--headless")  # Enable headless mode
firefox_options.add_argument("--disable-gpu") # Recommended for headless mode
firefox_options.add_argument("--window-size=1920x1080") # Set a window size
firefox_options.add_argument("--no-sandbox") # Required if running as root in some environments
firefox_options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems

# Initialize Firefox WebDriver
# Make sure geckodriver is in your PATH or specify its path if necessary
# If geckodriver is installed via pkg, it should be in PATH by default.
driver = webdriver.Firefox(options=firefox_options)

try:
    driver.get(url)
except Exception as e:
    print(f"Error accessing URL: {e}")
    driver.quit()
    exit()

print("Navigated to URL. Looking for login link...")
while True:
    try:
        login_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginlink")))
        print("Login link found.")
        break
    except:
        print("Login link not found, retrying...")
        # You might want to add a small sleep here to avoid busy-waiting
        # import time
        # time.sleep(1)
        pass # Keep trying until found or timeout

try:
    login_link.click()
    print("Clicked login link.")
except Exception as e:
    print(f"Error clicking login link: {e}")
    driver.quit()
    exit()

try:
    # Wait for the username field to be present after clicking login
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "txtUsr"))
    )
    print("Username field found.")
except Exception as e:
    print(f"Error finding username field: {e}")
    driver.quit()
    exit()

try:
    password_field = driver.find_element(By.ID, "txtPwd") # Assuming txtPwd appears with txtUsr
    print("Password field found.")
except Exception as e:
    print(f"Error finding password field: {e}")
    driver.quit()
    exit()

try:
    username_field.send_keys("user")
    print("Entered username.")
except Exception as e:
    print(f"Error entering username: {e}")
    driver.quit()
    exit()

try:
    password_field.send_keys("@l03e1t3")
    print("Entered password.")
except Exception as e:
    print(f"Error entering password: {e}")
    driver.quit()
    exit()

try:
    # Click the login button
    driver.find_element(By.ID, "btnLogin").click()
    print("Clicked login button.")
except Exception as e:
    print(f"Error clicking login button: {e}")
    driver.quit()
    exit()

try:
    # Wait for the restart button to be clickable after successful login
    restart_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Restart Device' and @type='button']")))
    print("Restart device button found.")
except Exception as e:
    print(f"Error finding restart device button: {e}")
    driver.quit()
    exit()

try:
    restart_button.click()
    print("Clicked restart device button.")
except Exception as e:
    print(f"Error clicking restart device button: {e}")
    driver.quit()
    exit()

try:
    restart_buttons = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "yesbtn")))
    print("Confirmation 'yes' button found.")
except Exception as e:
    print(f"Error finding confirmation 'yes' button: {e}")
    driver.quit()
    exit()

try:
    restart_buttons.click()
    print("Clicked confirmation 'yes' button.")
except Exception as e:
    print(f"Error clicking confirmation 'yes' button: {e}")
    # Continue to finally block even if this fails
    pass
finally:
    print("Airplane Mode Done (or restart process initiated).")
    driver.quit()
    print("WebDriver closed.")
