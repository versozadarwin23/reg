from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager # Ito ang bagong import
import threading

app = Flask(__name__)

def run_selenium_task():
    url = "http://192.168.254.254/index.html#index_status"

    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Optional: Ito ay para maiwasan ang ilang common issues sa headless mode
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None

    try:
        # Initialize Chrome WebDriver using ChromeDriverManager
        # Ito ang papalitan ang 'Service(executable_path=...)'
        driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)

        print("Navigated to URL. Looking for login link...")
        while True:
            try:
                login_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginlink")))
                print("Login link found.")
                break
            except:
                print("Login link not found, retrying...")
                pass

        login_link.click()
        print("Clicked login link.")

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtUsr"))
        )
        print("Username field found.")

        password_field = driver.find_element(By.ID, "txtPwd")
        print("Password field found.")

        username_field.send_keys("user")
        print("Entered username.")

        password_field.send_keys("@l03e1t3")
        print("Entered password.")

        driver.find_element(By.ID, "btnLogin").click()
        print("Clicked login button.")

        restart_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Restart Device' and @type='button']"))
        )
        print("Restart device button found.")

        restart_button.click()
        print("Clicked restart device button.")

        restart_confirm = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "yesbtn"))
        )
        print("Confirmation 'yes' button found.")

        restart_confirm.click()
        print("Clicked confirmation 'yes' button.")
        print("Airplane Mode Done (or restart process initiated).")
        return {"status": "success", "message": "Selenium task completed successfully."}

    except Exception as e:
        print(f"An error occurred during Selenium execution: {e}")
        return {"status": "error", "message": f"Selenium task failed: {e}"}
    finally:
        if driver:
            driver.quit()
            print("WebDriver closed.")

---

## Basic Flask App Example

```python
@app.route('/')
def home():
    return "Welcome to the Selenium Flask App! Go to /run-selenium to trigger the task."

@app.route('/run-selenium')
def trigger_selenium():
    thread = threading.Thread(target=run_selenium_task)
    thread.start()
    return jsonify({"message": "Selenium task initiated in the background. Check server console for logs."})

if __name__ == '__main__':
    app.run(debug=True)
